import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.compose import TransformedTargetRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import logging
from typing import Dict, Any, Optional, List
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class MLModel:
    def __init__(self, model_path: str = "models/car_price_model.joblib"):
        self.model_path = model_path
        self.model = None
        self.preprocessor = None
        self.feature_columns: List[str] = []
        self.is_trained = False
        
        # Try to load existing model
        self.load_model()
    
    def preprocess_data(self, df: pd.DataFrame, is_training: bool = True) -> pd.DataFrame:
        """Preprocess the data for training or prediction"""
        df_processed = df.copy()

        # Ensure numeric conversion
        if 'Year' in df_processed.columns:
            df_processed['Year'] = pd.to_numeric(df_processed['Year'], errors='coerce')
        if 'KM_Driven' in df_processed.columns:
            df_processed['KM_Driven'] = pd.to_numeric(df_processed['KM_Driven'], errors='coerce')

        # Create engineered features
        if 'Year' in df_processed.columns:
            current_year = datetime.now().year
            df_processed['Car_Age'] = current_year - df_processed['Year']

        if 'KM_Driven' in df_processed.columns:
            # avoid division by zero
            df_processed['KM_Per_Year'] = df_processed['KM_Driven'] / (df_processed.get('Car_Age', 1).replace(0, 1) + 1)

        # Fill numeric NaNs with median during training or 0 during prediction
        num_cols = ['Year', 'KM_Driven', 'Car_Age', 'KM_Per_Year']
        for col in num_cols:
            if col in df_processed.columns:
                if is_training:
                    df_processed[col].fillna(df_processed[col].median(), inplace=True)
                else:
                    df_processed[col].fillna(0, inplace=True)

        return df_processed
    
    def train(self, df: pd.DataFrame) -> float:
        """Train the ML model"""
        try:
            logger.info("Starting model training...")
            
            # Validate required columns
            required_columns = ['Brand', 'Model', 'Year', 'KM_Driven', 'Fuel', 
                               'Seller_Type', 'Transmission', 'Owner', 'Selling_Price']
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Remove rows with missing target values
            df_clean = df.dropna(subset=['Selling_Price']).copy()
            
            # Remove outliers in selling price (optional)
            Q1 = df_clean['Selling_Price'].quantile(0.25)
            Q3 = df_clean['Selling_Price'].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Keep reasonable price range (adjust based on Morocco car market)
            df_clean = df_clean[
                (df_clean['Selling_Price'] >= max(10000, lower_bound)) & 
                (df_clean['Selling_Price'] <= min(2000000, upper_bound))
            ]
            
            logger.info(f"Training with {len(df_clean)} samples after cleaning")
            
            # Preprocess data
            df_processed = self.preprocess_data(df_clean, is_training=True)

            # Define feature columns (original column names expected by the preprocessor)
            feature_columns = ['Brand', 'Model', 'Fuel', 'Seller_Type', 'Transmission', 'Owner',
                               'Year', 'KM_Driven', 'Car_Age', 'KM_Per_Year']

            # Keep only available columns
            available_columns = [col for col in feature_columns if col in df_processed.columns]
            self.feature_columns = available_columns

            X = df_processed[self.feature_columns]
            y = df_processed['Selling_Price']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Build preprocessing pipeline
            categorical_ohe = [c for c in ['Brand', 'Fuel', 'Seller_Type', 'Transmission', 'Owner'] if c in self.feature_columns]
            model_cardinality = [c for c in ['Model'] if c in self.feature_columns]

            transformers = []
            if categorical_ohe:
                transformers.append(('ohe', OneHotEncoder(handle_unknown='ignore', sparse=False), categorical_ohe))
            if model_cardinality:
                transformers.append(('model_ord', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1), model_cardinality))

            # ColumnTransformer: OHE for low-cardinality cats, ordinal for Model, pass through numeric
            preprocessor = ColumnTransformer(transformers=transformers, remainder='passthrough')
            self.preprocessor = preprocessor

            # Use TransformedTargetRegressor with log1p to reduce skew on prices
            rf_base = RandomForestRegressor(n_estimators=200, max_depth=12, min_samples_leaf=2, max_features='sqrt', random_state=42, n_jobs=-1)
            gb_base = GradientBoostingRegressor(n_estimators=200, max_depth=8, learning_rate=0.05, random_state=42)

            rf_pipeline = Pipeline([('preprocessor', preprocessor), ('est', rf_base)])
            gb_pipeline = Pipeline([('preprocessor', preprocessor), ('est', gb_base)])

            rf_ttr = TransformedTargetRegressor(regressor=rf_pipeline, func=np.log1p, inverse_func=np.expm1)
            gb_ttr = TransformedTargetRegressor(regressor=gb_pipeline, func=np.log1p, inverse_func=np.expm1)

            # Fit both models
            rf_ttr.fit(X_train, y_train)
            gb_ttr.fit(X_train, y_train)

            # Save ensemble
            self.model = {'rf': rf_ttr, 'gb': gb_ttr, 'weights': [0.6, 0.4]}
            
            # Evaluate model
            rf_pred = self.model['rf'].predict(X_test)
            gb_pred = self.model['gb'].predict(X_test)
            ensemble_pred = (self.model['weights'][0] * rf_pred + self.model['weights'][1] * gb_pred)
            
            # Calculate metrics
            mae = mean_absolute_error(y_test, ensemble_pred)
            r2 = r2_score(y_test, ensemble_pred)
            
            # Calculate accuracy as percentage (lower MAE relative to mean price = higher accuracy)
            mean_price = y_test.mean()
            accuracy = max(0, (1 - mae / mean_price)) * 100
            
            self.is_trained = True
            
            # Save model
            self.save_model()
            
            logger.info(f"Model trained successfully. R2: {r2:.3f}, MAE: {mae:.0f}, Accuracy: {accuracy:.1f}%")
            
            return accuracy
            
        except Exception as e:
            logger.error(f"Error during training: {str(e)}")
            raise
    
    def predict(self, car_data) -> Dict[str, Any]:
        """Make prediction for a single car"""
        if not self.is_trained or not self.model:
            raise ValueError("Model is not trained")
        
        try:
            # Convert input to DataFrame
            if hasattr(car_data, 'dict'):
                # Pydantic model
                data_dict = car_data.dict()
            else:
                # Dictionary
                data_dict = car_data
            
            df = pd.DataFrame([data_dict])

            # Preprocess engineered features
            df_processed = self.preprocess_data(df, is_training=False)

            # Ensure we provide the same feature columns used in training
            missing_cols = [c for c in self.feature_columns if c not in df_processed.columns]
            for c in missing_cols:
                df_processed[c] = 0

            X = df_processed[self.feature_columns]

            # Make predictions with ensemble (pipelines handle preprocessing and target inverse transform)
            rf_pred = self.model['rf'].predict(X)[0]
            gb_pred = self.model['gb'].predict(X)[0]
            
            ensemble_pred = (self.model['weights'][0] * rf_pred + 
                           self.model['weights'][1] * gb_pred)
            
            # Calculate confidence based on individual model agreement
            pred_diff = abs(rf_pred - gb_pred)
            max_diff = max(rf_pred, gb_pred) * 0.3  # 30% difference threshold
            confidence = max(0.5, 1 - (pred_diff / max_diff)) if max_diff > 0 else 0.9
            
            result = {
                'price': max(10000, float(ensemble_pred)),  # Minimum reasonable price
                'confidence': min(0.95, confidence),  # Cap confidence at 95%
                'rf_prediction': rf_pred,
                'gb_prediction': gb_pred
            }
            
            logger.info(f"Prediction: {result['price']:.0f} MAD (confidence: {result['confidence']:.2f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            raise
    
    def save_model(self):
        """Save the trained model and encoders"""
        if self.model and self.is_trained:
            model_data = {
                'model': self.model,
                'preprocessor': self.preprocessor,
                'feature_columns': self.feature_columns,
                'is_trained': self.is_trained,
                'timestamp': datetime.now().isoformat()
            }
            joblib.dump(model_data, self.model_path)
            logger.info(f"Model saved to {self.model_path}")
    
    def load_model(self):
        """Load a pre-trained model"""
        if os.path.exists(self.model_path):
            try:
                model_data = joblib.load(self.model_path)
                self.model = model_data['model']
                self.preprocessor = model_data.get('preprocessor')
                self.feature_columns = model_data['feature_columns']
                self.is_trained = model_data['is_trained']
                
                logger.info(f"Model loaded from {self.model_path}")
                return True
            except Exception as e:
                logger.warning(f"Failed to load model: {str(e)}")
                return False
        return False
    
    def is_loaded(self) -> bool:
        """Check if model is loaded and ready"""
        return self.is_trained and self.model is not None
    
    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """Get feature importance from the model"""
        if not self.is_loaded():
            return None
        
        try:
            # Extract underlying RandomForest from the pipeline inside TransformedTargetRegressor
            rf_ttr = self.model['rf']
            reg_pipeline = getattr(rf_ttr, 'regressor_', None)
            if reg_pipeline is None:
                return None

            # pipeline structure: preprocessor -> est
            preproc = reg_pipeline.named_steps.get('preprocessor')
            est = reg_pipeline.named_steps.get('est')

            if est is None:
                return None

            rf_importance = getattr(est, 'feature_importances_', None)
            if rf_importance is None:
                return None

            # Build feature names after preprocessing
            try:
                # ColumnTransformer supports get_feature_names_out in modern sklearn
                feature_names = preproc.get_feature_names_out(self.feature_columns)
                # If remainder='passthrough', some names may be like 'remainder__<col>' - handle gracefully
                feature_names = [fn.replace('remainder__', '') for fn in feature_names]
            except Exception:
                # Fallback: return importances mapped to numeric/raw feature names
                feature_names = self.feature_columns

            importance_dict = {}
            for i, fname in enumerate(feature_names[:len(rf_importance)]):
                importance_dict[fname] = float(rf_importance[i])

            return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
            
        except Exception as e:
            logger.error(f"Error getting feature importance: {str(e)}")
            return None
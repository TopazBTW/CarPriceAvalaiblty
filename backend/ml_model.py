import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import logging
from typing import Dict, Any, Optional
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class MLModel:
    def __init__(self, model_path: str = "car_price_model.joblib"):
        self.model_path = model_path
        self.model = None
        self.encoders = {}
        self.feature_columns = []
        self.is_trained = False
        
        # Try to load existing model
        self.load_model()
    
    def preprocess_data(self, df: pd.DataFrame, is_training: bool = True) -> pd.DataFrame:
        """Preprocess the data for training or prediction"""
        df_processed = df.copy()
        
        # Define categorical columns that need encoding
        categorical_columns = ['Brand', 'Model', 'Fuel', 'Seller_Type', 'Transmission', 'Owner']
        
        # Handle categorical encoding
        for col in categorical_columns:
            if col in df_processed.columns:
                if is_training:
                    # Create and fit encoder during training
                    self.encoders[col] = LabelEncoder()
                    df_processed[col] = self.encoders[col].fit_transform(df_processed[col].astype(str))
                else:
                    # Use existing encoder for prediction
                    if col in self.encoders:
                        # Handle unknown categories
                        try:
                            df_processed[col] = self.encoders[col].transform(df_processed[col].astype(str))
                        except ValueError:
                            # Handle unknown labels by assigning them to the most common class
                            known_classes = set(self.encoders[col].classes_)
                            df_processed[col] = df_processed[col].apply(
                                lambda x: x if x in known_classes else self.encoders[col].classes_[0]
                            )
                            df_processed[col] = self.encoders[col].transform(df_processed[col].astype(str))
                    else:
                        # If encoder doesn't exist, use default value
                        df_processed[col] = 0
        
        # Handle numeric columns
        numeric_columns = ['Year', 'KM_Driven']
        for col in numeric_columns:
            if col in df_processed.columns:
                df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')
                df_processed[col].fillna(df_processed[col].median() if is_training else 0, inplace=True)
        
        # Create additional features
        if 'Year' in df_processed.columns:
            current_year = datetime.now().year
            df_processed['Car_Age'] = current_year - df_processed['Year']
        
        if 'KM_Driven' in df_processed.columns:
            df_processed['KM_Per_Year'] = df_processed['KM_Driven'] / (df_processed.get('Car_Age', 1) + 1)
        
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
            
            # Prepare features and target
            feature_columns = ['Brand', 'Model', 'Year', 'KM_Driven', 'Fuel', 
                              'Seller_Type', 'Transmission', 'Owner', 'Car_Age', 'KM_Per_Year']
            
            # Filter only available columns
            available_columns = [col for col in feature_columns if col in df_processed.columns]
            self.feature_columns = available_columns
            
            X = df_processed[self.feature_columns]
            y = df_processed['Selling_Price']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train ensemble model
            # Use both RandomForest and GradientBoosting, then average predictions
            rf_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
            
            gb_model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=8,
                learning_rate=0.1,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
            
            # Train both models
            rf_model.fit(X_train, y_train)
            gb_model.fit(X_train, y_train)
            
            # Create ensemble
            self.model = {
                'rf': rf_model,
                'gb': gb_model,
                'weights': [0.6, 0.4]  # Give more weight to RandomForest
            }
            
            # Evaluate model
            rf_pred = rf_model.predict(X_test)
            gb_pred = gb_model.predict(X_test)
            ensemble_pred = (self.model['weights'][0] * rf_pred + 
                           self.model['weights'][1] * gb_pred)
            
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
            
            # Preprocess
            df_processed = self.preprocess_data(df, is_training=False)
            
            # Ensure all required features are present
            X = df_processed[self.feature_columns]
            
            # Make predictions with ensemble
            rf_pred = self.model['rf'].predict(X)[0]
            gb_pred = self.model['gb'].predict(X)[0]
            
            ensemble_pred = (self.model['weights'][0] * rf_pred + 
                           self.model['weights'][1] * gb_pred)
            
            # Calculate confidence based on individual model agreement
            pred_diff = abs(rf_pred - gb_pred)
            max_diff = max(rf_pred, gb_pred) * 0.3  # 30% difference threshold
            confidence = max(0.5, 1 - (pred_diff / max_diff)) if max_diff > 0 else 0.9
            
            result = {
                'price': max(10000, ensemble_pred),  # Minimum reasonable price
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
                'encoders': self.encoders,
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
                self.encoders = model_data['encoders']
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
            # Get importance from RandomForest (primary model)
            rf_importance = self.model['rf'].feature_importances_
            
            importance_dict = {}
            for i, feature in enumerate(self.feature_columns):
                importance_dict[feature] = float(rf_importance[i])
            
            # Sort by importance
            return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
            
        except Exception as e:
            logger.error(f"Error getting feature importance: {str(e)}")
            return None
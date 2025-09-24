from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import joblib
import logging
from typing import List, Optional, Dict, Any
import json
from datetime import datetime, timedelta
import asyncio
import aiohttp
from scrapers import fetch_avito_listings, fetch_moteur_listings, compute_average_price
from enhanced_scrapers import get_enhanced_market_data
from comprehensive_scraper import get_comprehensive_morocco_prices
from advanced_morocco_scraper import get_advanced_morocco_prices
from robust_morocco_scraper import get_robust_morocco_prices
from production_scraper import get_production_morocco_prices
from real_morocco_prices import get_real_morocco_price, MOROCCO_REAL_PRICES
from ml_model import MLModel
import os
from cachetools import TTLCache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Morocco Car Price Prediction API", version="1.0.0")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache for storing scraping results (TTL: 15 minutes)
listings_cache = TTLCache(maxsize=1000, ttl=900)  # 15 minutes TTL

# ML Model instance
ml_model = MLModel()

class CarPredictionRequest(BaseModel):
    Brand: str
    Model: str
    Year: int
    KM_Driven: int
    Fuel: str
    Seller_Type: str
    Transmission: str
    Owner: str

class CarListing(BaseModel):
    title: str
    price: int
    url: str

class PredictionResponse(BaseModel):
    predicted_price: int
    currency: str
    market_avg_price: Optional[int]
    listings: List[CarListing]
    model_confidence: float
    scraping_source: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    model_loaded: bool
    scraping_enabled: bool

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        model_loaded=ml_model.is_loaded(),
        scraping_enabled=True
    )

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload CSV file to train the ML model"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Read CSV file
        contents = await file.read()
        with open(f"temp_{file.filename}", "wb") as f:
            f.write(contents)
        
        # Load and train model
        df = pd.read_csv(f"temp_{file.filename}")
        
        # Validate required columns
        required_columns = ['Brand', 'Model', 'Year', 'KM_Driven', 'Fuel', 
                           'Seller_Type', 'Transmission', 'Owner', 'Selling_Price']
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {missing_columns}"
            )
        
        # Train the model
        accuracy = ml_model.train(df)
        
        # Clean up temp file
        os.remove(f"temp_{file.filename}")
        
        logger.info(f"Model trained successfully with accuracy: {accuracy}")
        
        return {
            "message": "Model trained successfully",
            "accuracy": accuracy,
            "training_samples": len(df),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error training model: {str(e)}")

@app.post("/predict", response_model=PredictionResponse)
async def predict_car_price(request: CarPredictionRequest):
    """
    Predict car price using ML model and fetch market data from Moroccan websites
    """
    try:
        logger.info(f"Prediction request for {request.Brand} {request.Model} {request.Year}")
        
        # Check if model is trained
        if not ml_model.is_loaded():
            raise HTTPException(status_code=400, detail="Model not trained. Please upload training data first.")
        
        # Déterminer l'état du véhicule selon Seller_Type
        vehicle_condition = "Neuf" if request.Seller_Type == "Dealer" else "Occasion"
        
        # Generate ML prediction
        ml_prediction = ml_model.predict(request)
        
        # Create cache key for scraping results
        cache_key = f"{request.Brand.lower()}_{request.Model.lower()}_{request.Year}_{vehicle_condition}"
        
        # Check cache first
        if cache_key in listings_cache:
            logger.info(f"Using cached market data for {cache_key}")
            cached_data = listings_cache[cache_key]
            market_data = cached_data
        else:
            # Utiliser d'abord les prix réels du marché marocain
            logger.info(f"Getting real Morocco market prices for {request.Brand} {request.Model} {request.Year} ({vehicle_condition})")
            
            real_market_data = get_real_morocco_price(
                request.Brand, request.Model, request.Year, vehicle_condition, request.KM_Driven
            )
            
            if real_market_data['market_price']:
                # On a des données réelles du marché
                market_data = {
                    'market_price': real_market_data['market_price'],
                    'confidence': 'high',  # Données officielle = haute confiance
                    'data_points': 1,
                    'price_range': real_market_data['price_range'],
                    'sample_listings': [],
                    'breakdown': {
                        'new_count': 1 if vehicle_condition == "Neuf" else 0,
                        'used_count': 1 if vehicle_condition == "Occasion" else 0,
                        'new_avg': real_market_data['market_price'] if vehicle_condition == "Neuf" else None,
                        'used_avg': real_market_data['market_price'] if vehicle_condition == "Occasion" else None
                    },
                    'sites_data': {'real_morocco_prices': {'count': 1, 'source': 'official'}}
                }
                
                # Cache les résultats pour 30 minutes
                listings_cache[cache_key] = market_data
                logger.info(f"Using real Morocco market data: {real_market_data['market_price']} MAD "
                           f"(range: {real_market_data['price_range'][0]}-{real_market_data['price_range'][1]})")
                
            else:
                # Fallback vers le scraping si pas de données réelles
                logger.info("No real market data found, trying production scraper with realistic data generation...")
                
                try:
                    # Utiliser le scraper de production qui combine scraping réel et génération de données réalistes
                    market_data = await get_production_morocco_prices(
                        request.Brand, request.Model, request.Year, vehicle_condition
                    )
                    
                    # Cache les résultats pour 20 minutes (data plus fraîche)
                    listings_cache[cache_key] = market_data
                    logger.info(f"Production scraper completed: {market_data['data_points']} listings "
                               f"(Real data: {market_data.get('real_data_found', False)}, "
                               f"Generated: {market_data.get('generated_listings', 0)}) - {vehicle_condition}")
                    
                except Exception as e:
                    logger.warning(f"Production scraper failed, trying robust scraper: {str(e)}")
                    
                    try:
                        # Fallback vers le scraper robuste qui gère mieux les protections anti-scraping
                        market_data = await get_robust_morocco_prices(
                            request.Brand, request.Model, request.Year, vehicle_condition
                        )
                        
                        # Cache les résultats pour 30 minutes
                        listings_cache[cache_key] = market_data
                        logger.info(f"Robust scraping completed: {market_data['data_points']} listings "
                                   f"from {len(market_data['sites_data'])} sites (condition: {vehicle_condition})")
                        
                    except Exception as e2:
                        logger.warning(f"Robust scraping failed, trying advanced scraper: {str(e2)}")
                        
                        try:
                            # Fallback vers le scraper avancé qui cible les sections dédiées
                            market_data = await get_advanced_morocco_prices(
                                request.Brand, request.Model, request.Year, vehicle_condition
                            )
                            
                            # Cache les résultats pour 45 minutes
                            listings_cache[cache_key] = market_data
                            logger.info(f"Advanced scraping completed: {market_data['data_points']} listings "
                                       f"from {len(market_data['sites_data'])} sites (condition: {vehicle_condition})")
                            
                        except Exception as e3:
                            logger.warning(f"Advanced scraping failed, trying comprehensive scraper: {str(e3)}")
                            
                            try:
                                market_data = await get_comprehensive_morocco_prices(
                                    request.Brand, request.Model, request.Year, vehicle_condition
                                )
                                
                                # Cache les résultats pour 1 heure
                                listings_cache[cache_key] = market_data
                                logger.info(f"Comprehensive scraping completed: {market_data['data_points']} listings "
                                           f"from {len(market_data['sites_data'])} sites "
                                           f"(New: {market_data['breakdown']['new_count']}, "
                                           f"Used: {market_data['breakdown']['used_count']})")
                                
                            except Exception as e4:
                                logger.warning(f"Comprehensive scraping failed, trying enhanced scraper: {str(e4)}")
                                
                                try:
                                    # Fallback vers enhanced scraper
                                    market_data = await get_enhanced_market_data(
                                        request.Brand, request.Model, request.Year, vehicle_condition
                                    )
                                    logger.info("Using enhanced scraper as fallback")
                                    
                                except Exception as e5:
                                    logger.warning(f"Enhanced scraping also failed, using basic scraper: {str(e5)}")
                    
                    # Dernier fallback vers scrapers basiques
                    try:
                        avito_listings = await fetch_avito_listings(request.Brand, request.Model, request.Year)
                        moteur_listings = await fetch_moteur_listings(request.Brand, request.Model, request.Year)
                        
                        all_listings = avito_listings + moteur_listings
                        market_avg = compute_average_price(all_listings) if all_listings else None
                        
                        market_data = {
                            'market_price': market_avg,
                            'confidence': 'medium' if all_listings else 'low',
                            'data_points': len(all_listings),
                            'sample_listings': all_listings[:5],
                            'breakdown': {'new_count': 0, 'used_count': len(all_listings), 'new_avg': None, 'used_avg': market_avg},
                            'sites_data': {'basic_scraper': {'count': len(all_listings)}}
                        }
                        
                    except Exception as e3:
                        logger.error(f"All scraping methods failed: {e3}")
                        market_data = {
                            'market_price': None,
                            'confidence': 'none',
                            'data_points': 0,
                            'sample_listings': [],
                            'breakdown': {'new_count': 0, 'used_count': 0, 'new_avg': None, 'used_avg': None},
                            'sites_data': {}
                        }
        
        # Ajuster la prédiction ML selon l'état et les données de marché
        final_prediction = ml_prediction['price']
        
        if market_data['market_price']:
            # Utiliser prioritairement les données de marché si on a assez de points de données
            if market_data['data_points'] >= 3:
                # Prioriser les données de marché
                market_weight = {
                    'high': 0.85,   # 85% marché, 15% ML si haute confiance
                    'medium': 0.65, # 65% marché, 35% ML si confiance moyenne  
                    'low': 0.35,    # 35% marché, 65% ML si faible confiance
                    'none': 0.0
                }.get(market_data['confidence'], 0.0)
            else:
                # Moins de confiance si peu de données
                market_weight = {
                    'high': 0.6,
                    'medium': 0.4,
                    'low': 0.2,
                    'none': 0.0
                }.get(market_data['confidence'], 0.0)
            
            ml_weight = 1.0 - market_weight
            
            # Si on a des données spécifiques neuf/occasion, les utiliser
            if vehicle_condition == "Neuf" and market_data['breakdown']['new_avg']:
                market_price = market_data['breakdown']['new_avg']
            elif vehicle_condition == "Occasion" and market_data['breakdown']['used_avg']:
                market_price = market_data['breakdown']['used_avg']
            else:
                market_price = market_data['market_price']
            
            final_prediction = int(
                (ml_prediction['price'] * ml_weight) + 
                (market_price * market_weight)
            )
            
            logger.info(f"Price calculation: ML={ml_prediction['price']} (weight={ml_weight:.2f}), "
                       f"Market={market_price} (weight={market_weight:.2f}), Final={final_prediction}")
        else:
            logger.info("No market data available, using ML prediction with condition adjustments")
        
        # Ajustements supplémentaires selon l'état et l'âge
        current_year = 2024
        age = current_year - request.Year
        
        if vehicle_condition == "Neuf":
            # Voitures neuves - prix généralement plus élevés
            if age <= 1:  # Vraiment neuve (2023-2024)
                final_prediction = int(final_prediction * 1.1)  # +10%
            else:  # "Neuf" mais d'une année précédente
                final_prediction = int(final_prediction * 1.05)  # +5%
        else:
            # Occasion - appliquer dépréciation
            km_factor = max(0.7, 1 - (request.KM_Driven / 250000) * 0.25)  # Dépréciation kilométrage
            age_factor = max(0.65, 1 - (age * 0.07))  # 7% de dépréciation par an
            
            # Facteur supplémentaire pour les voitures très anciennes
            if age > 8:
                age_factor *= 0.9
            
            final_prediction = int(final_prediction * km_factor * age_factor)
            
            logger.info(f"Occasion adjustments: age={age}y (factor={age_factor:.2f}), "
                       f"km={request.KM_Driven} (factor={km_factor:.2f})")
        
        # S'assurer que le prix reste raisonnable
        final_prediction = max(30000, min(3000000, final_prediction))
        
        # Prepare response with sample listings
        car_listings = []
        sample_listings = market_data.get('sample_listings', [])
        
        for listing in sample_listings[:3]:  # Top 3 listings
            if isinstance(listing, dict) and 'title' in listing:
                car_listings.append(CarListing(
                    title=listing['title'],
                    price=listing['price'],
                    url=listing.get('url', f"https://www.avito.ma/search?q={request.Brand}+{request.Model}")
                ))
        
        # Calculer la confiance globale
        overall_confidence = min(
            ml_prediction['confidence'],
            {'high': 0.9, 'medium': 0.7, 'low': 0.5, 'none': 0.3}.get(market_data['confidence'], 0.3)
        )
        
        response = PredictionResponse(
            predicted_price=final_prediction,
            currency="MAD",
            market_avg_price=market_data.get('market_price'),
            listings=car_listings,
            model_confidence=overall_confidence,
            scraping_source=f"enhanced_scraper_{market_data['data_points']}_points"
        )
        
        logger.info(f"Prediction completed: Final={final_prediction}, Condition={vehicle_condition}, Confidence={overall_confidence:.2f}")
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Morocco Car Price Prediction API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "upload": "/upload-csv",
            "predict": "/predict"
        },
        "documentation": "/docs"
    }


@app.get('/brands')
async def list_brands():
    """Return authoritative brand list from real Morocco price DB"""
    try:
        brands = list(MOROCCO_REAL_PRICES.keys())
        return {"brands": brands}
    except Exception as e:
        logger.error(f"Error listing brands: {e}")
        raise HTTPException(status_code=500, detail="Unable to list brands")


@app.get('/brands/{brand}/models')
async def list_brand_models(brand: str):
    """Return models and available years for a given brand based on real Morocco DB"""
    try:
        brand_data = MOROCCO_REAL_PRICES.get(brand)
        if not brand_data:
            raise HTTPException(status_code=404, detail="Brand not found")

        models = []
        for model_name, model_data in brand_data.items():
            # collect years from both 'new' and 'used' sections
            years = set()
            new_section = model_data.get('new', {})
            used_section = model_data.get('used', {})
            years.update(new_section.keys())
            years.update(used_section.keys())

            models.append({
                'model': model_name,
                'available_years': sorted(list(years), reverse=True)
            })

        return {"brand": brand, "models": models}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing models for {brand}: {e}")
        raise HTTPException(status_code=500, detail="Unable to list models")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
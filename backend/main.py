#!/usr/bin/env python3
"""
🚗 MOROCCO CAR PRICE PREDICTION API - OPTIMIZED VERSION
Clean, efficient backend with proper data handling
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import logging
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
import aiohttp
import os
import re
from urllib.parse import quote
from pathlib import Path
from bs4 import BeautifulSoup
from cachetools import TTLCache

# Import our modules
from models.ml_model import MLModel
from scrapers.real_morocco_prices import get_real_morocco_price
from scrapers.production_scraper import get_production_morocco_prices
from kifal_features import add_kifal_endpoints, KifalStyleService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Morocco Car Price Prediction API", version="2.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache for storing results (TTL: 15 minutes)
cache = TTLCache(maxsize=1000, ttl=900)

# ML Model instance
ml_model = MLModel()

# Load clean Kifal.ma car data
CLEAN_CAR_DATA = {}
CLEAN_BRANDS_DATA = {}
CLEAN_BRANDS = []

try:
    # Load complete car data from Kifal.ma
    with open('data/json/morocco_cars_clean.json', 'r', encoding='utf-8') as f:
        CLEAN_CAR_DATA = json.load(f)
    
    # Load brands data from Kifal.ma
    with open('data/json/morocco_brands_clean.json', 'r', encoding='utf-8') as f:
        CLEAN_BRANDS_DATA = json.load(f)
        CLEAN_BRANDS = [brand['name'] for brand in CLEAN_BRANDS_DATA['brands']]
    
    logger.info(f"✅ Loaded Kifal.ma data: {len(CLEAN_BRANDS)} brands, "
               f"{len(CLEAN_CAR_DATA.get('models', {}))} models, "
               f"{len(CLEAN_CAR_DATA.get('cars', []))} cars")
    
except FileNotFoundError as e:
    logger.warning(f"❌ Kifal.ma clean data files not found: {e}")
    CLEAN_CAR_DATA = {}
    CLEAN_BRANDS_DATA = {}
    CLEAN_BRANDS = []

# Pydantic models
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
    clean_data_loaded: bool
    total_brands: int
    total_models: int

@app.get("/", response_model=Dict[str, Any])
async def root():
    """API root endpoint"""
    return {
        "message": "Morocco Car Price Prediction API",
        "version": "2.0.0",
        "status": "optimized and clean",
        "endpoints": {
            "health": "/health",
            "brands": "/brands",
            "predict": "/predict",
            "documentation": "/docs"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with Kifal.ma data stats"""
    total_models = len(CLEAN_CAR_DATA.get('models', {})) if CLEAN_CAR_DATA else 0
    total_brands = len(CLEAN_BRANDS) if CLEAN_BRANDS else 0
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        model_loaded=ml_model.is_loaded(),
        clean_data_loaded=bool(CLEAN_CAR_DATA and CLEAN_BRANDS_DATA),
        total_brands=total_brands,
        total_models=total_models
    )

@app.get("/brands")
async def get_brands(condition: Optional[str] = None, category: Optional[str] = None):
    """Get clean list of car brands from Kifal.ma data"""
    
    if not CLEAN_BRANDS_DATA:
        return {"brands": [], "source": "no_data", "count": 0}
    
    brands_list = CLEAN_BRANDS_DATA['brands']
    
    if category:
        # Filter by category (premium, generaliste, chinese, electric, etc.)
        filtered_brands = [
            brand['name'] for brand in brands_list 
            if brand.get('category') == category.lower()
        ]
        return {
            "brands": sorted(filtered_brands), 
            "source": f"kifal_category_{category}", 
            "count": len(filtered_brands),
            "category": category
        }
    
    elif condition == "neuf":
        # Return all brands for new cars
        brands = [brand['name'] for brand in brands_list]
        logger.info(f"Returning {len(brands)} Kifal.ma brands for Neuf condition")
        return {
            "brands": sorted(brands), 
            "source": "kifal_neuf", 
            "count": len(brands)
        }
    
    elif condition == "occasion":
        # Return brands that have car data available
        available_brands = [brand for brand in CLEAN_BRANDS if brand in CLEAN_CAR_DATA.get('brands', {})]
        return {
            "brands": sorted(available_brands), 
            "source": "kifal_occasion", 
            "count": len(available_brands)
        }
    
    else:
        # Return all available brands
        return {
            "brands": sorted(CLEAN_BRANDS), 
            "source": "kifal_all", 
            "count": len(CLEAN_BRANDS)
        }

@app.get("/brands/categories")
async def get_brand_categories():
    """Get all brand categories from Kifal.ma data"""
    if not CLEAN_BRANDS_DATA or 'categories' not in CLEAN_BRANDS_DATA:
        return {"categories": {}, "source": "no_data"}
    
    categories = {}
    for category, brands in CLEAN_BRANDS_DATA['categories'].items():
        categories[category] = {
            "count": len(brands),
            "brands": [brand['name'] for brand in brands]
        }
    
    return {
        "categories": categories,
        "total_categories": len(categories),
        "source": "kifal_data"
    }

@app.get("/brands/{brand}/models")
async def get_brand_models(brand: str):
    """Get models for a specific brand from Kifal.ma data"""
    brand_upper = brand.upper()
    
    if not CLEAN_CAR_DATA or 'models' not in CLEAN_CAR_DATA:
        return {
            "brand": brand_upper,
            "models": [],
            "count": 0,
            "source": "no_data"
        }
    
    brand_models = CLEAN_CAR_DATA['models'].get(brand_upper, {})
    if brand_models:
        models = list(brand_models.keys())
        return {
            "brand": brand_upper,
            "models": sorted(models),
            "count": len(models),
            "source": "kifal_data"
        }
    else:
        # Return empty if brand not found
        return {
            "brand": brand_upper,
            "models": [],
            "count": 0,
            "source": "brand_not_found"
        }

@app.get("/brands/{brand}/models/{model}/listings")
async def get_model_listings(brand: str, model: str, limit: int = 10):
    """Get listings for a specific brand and model from Kifal.ma data"""
    brand_upper = brand.upper()
    model_upper = model.upper()
    
    if not CLEAN_CAR_DATA or 'cars' not in CLEAN_CAR_DATA:
        return {
            "brand": brand_upper,
            "model": model_upper,
            "listings": [],
            "count": 0,
            "total_available": 0,
            "source": "no_data"
        }
    
    # Filter cars by brand and model
    matching_cars = [
        car for car in CLEAN_CAR_DATA['cars']
        if car.get('brand', '').upper() == brand_upper and 
           car.get('model', '').upper() == model_upper
    ]
    
    if matching_cars:
        limited_listings = matching_cars[:limit]
        return {
            "brand": brand_upper,
            "model": model_upper,
            "listings": limited_listings,
            "count": len(limited_listings),
            "total_available": len(matching_cars),
            "source": "kifal_data"
        }
    else:
        return {
            "brand": brand_upper,
            "model": model_upper,
            "listings": [],
            "count": 0,
            "total_available": 0,
            "source": "no_matching_cars"
        }

@app.post("/predict", response_model=PredictionResponse)
async def predict_car_price(request: CarPredictionRequest):
    """Predict car price using clean data and ML model"""
    
    try:
        # Validate request
        if not all([request.Brand, request.Model, str(request.Year)]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Create cache key
        vehicle_condition = "Neuf" if request.Seller_Type == "Dealer" else "Occasion"
        cache_key = f"{request.Brand.lower()}_{request.Model.lower()}_{request.Year}_{vehicle_condition}"
        
        # Check cache
        if cache_key in cache:
            logger.info(f"Using cached data for {cache_key}")
            return cache[cache_key]
        
        # 1. Try real Morocco prices first
        logger.info(f"Getting real Morocco prices for {request.Brand} {request.Model} {request.Year}")
        
        real_market_data = get_real_morocco_price(
            request.Brand, request.Model, request.Year, vehicle_condition, request.KM_Driven
        )
        
        if real_market_data.get('market_price'):
            # Use real market data
            predicted_price = real_market_data['market_price']
            source = "real_morocco_prices"
            confidence = 0.95
            listings = []
            
            logger.info(f"Using real market price: {predicted_price} MAD")
            
        else:
            # 2. Try production scraper
            logger.info("No real market data, trying production scraper...")
            
            try:
                market_data = await get_production_morocco_prices(
                    request.Brand, request.Model, request.Year, vehicle_condition
                )
                
                if market_data.get('market_price'):
                    predicted_price = market_data['market_price']
                    source = "production_scraper"
                    confidence = 0.85
                    listings = market_data.get('sample_listings', [])[:5]
                    
                    logger.info(f"Using production scraper price: {predicted_price} MAD")
                else:
                    raise Exception("No production scraper data")
                    
            except Exception as e:
                logger.info(f"Production scraper failed: {e}, using ML model...")
                
                # 3. Fallback to ML model
                try:
                    # Prepare ML model input
                    input_data = pd.DataFrame([{
                        'Brand': request.Brand,
                        'Model': request.Model,
                        'Year': request.Year,
                        'KM_Driven': request.KM_Driven,
                        'Fuel': request.Fuel,
                        'Seller_Type': request.Seller_Type,
                        'Transmission': request.Transmission,
                        'Owner': request.Owner
                    }])
                    
                    predicted_price = int(ml_model.predict(input_data)[0])
                    source = "ml_model"
                    confidence = 0.75
                    listings = []
                    
                    logger.info(f"Using ML model prediction: {predicted_price} MAD")
                    
                except Exception as ml_error:
                    logger.error(f"ML model prediction failed: {ml_error}")
                    raise HTTPException(status_code=500, detail="Unable to predict price")
        
        # Create response
        response = PredictionResponse(
            predicted_price=predicted_price,
            currency="MAD",
            market_avg_price=predicted_price,
            listings=[CarListing(**listing) for listing in listings],
            model_confidence=confidence,
            scraping_source=source
        )
        
        # Cache the result
        cache[cache_key] = response
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error predicting car price: {e}")
        raise HTTPException(status_code=500, detail="Prediction error")

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload CSV file to retrain ML model"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be CSV")
        
        # Save uploaded file
        contents = await file.read()
        temp_file = f"temp_{file.filename}"
        
        with open(temp_file, "wb") as f:
            f.write(contents)
        
        # Load and train model
        df = pd.read_csv(temp_file)
        ml_model.train(df)
        
        # Clean up temp file
        os.remove(temp_file)
        
        logger.info(f"Model retrained with {len(df)} samples from {file.filename}")
        
        return {
            "message": "Model trained successfully",
            "samples": len(df),
            "file": file.filename
        }
        
    except Exception as e:
        logger.error(f"Error uploading CSV: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")

# Development endpoint for testing
@app.get("/debug/stats")
async def debug_stats():
    """Debug endpoint showing Kifal.ma data statistics"""
    stats = {
        "kifal_brands_count": len(CLEAN_BRANDS),
        "kifal_brands_data_loaded": bool(CLEAN_BRANDS_DATA),
        "kifal_car_data_loaded": bool(CLEAN_CAR_DATA),
        "cache_size": len(cache),
        "ml_model_loaded": ml_model.is_loaded()
    }
    
    if CLEAN_CAR_DATA:
        stats["total_brands"] = len(CLEAN_CAR_DATA.get('brands', {}))
        stats["total_models"] = len(CLEAN_CAR_DATA.get('models', {}))
        stats["total_cars"] = len(CLEAN_CAR_DATA.get('cars', []))
        stats["sample_brands"] = CLEAN_BRANDS[:5] if CLEAN_BRANDS else []
        
    if CLEAN_BRANDS_DATA:
        categories = CLEAN_BRANDS_DATA.get('categories', {})
        stats["brand_categories"] = {cat: len(brands) for cat, brands in categories.items()}
        stats["metadata"] = CLEAN_CAR_DATA.get('metadata', {})
    
    return stats

# Add Kifal.ma style features
add_kifal_endpoints(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
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
from ml_model import MLModel
from real_morocco_prices import get_real_morocco_price
from production_scraper import get_production_morocco_prices

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

# Load clean car data
CLEAN_CAR_DATA = {}
try:
    with open('car_data_clean_final.json', 'r', encoding='utf-8') as f:
        CLEAN_CAR_DATA = json.load(f)
    logger.info(f"Loaded clean car data: {len(CLEAN_CAR_DATA)} brands, "
               f"{sum(len(models) for models in CLEAN_CAR_DATA.values())} models")
except FileNotFoundError:
    logger.warning("Clean car data file not found, using fallback data")

# Load clean brands from HTML carousel
def get_clean_brands_from_html():
    """Extract clean brand list from HTML carousel"""
    try:
        with open('wandaloo_marques.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        carousel = soup.find('div', {'class': 'owl-carousel'})
        
        if not carousel:
            return []
        
        brands = []
        for link in carousel.find_all('a', href=True):
            href = link.get('href', '')
            if '/neuf/' in href and '/marque/' in href:
                brand_name = link.get_text(strip=True)
                if brand_name and len(brand_name) > 1:
                    brands.append(brand_name.upper())
        
        return sorted(list(set(brands)))
    except Exception as e:
        logger.error(f"Error loading brands from HTML: {e}")
        return []

CLEAN_BRANDS = get_clean_brands_from_html()

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
    """Health check endpoint"""
    total_models = sum(len(models) for models in CLEAN_CAR_DATA.values()) if CLEAN_CAR_DATA else 0
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        model_loaded=ml_model.is_loaded(),
        clean_data_loaded=bool(CLEAN_CAR_DATA),
        total_brands=len(CLEAN_CAR_DATA),
        total_models=total_models
    )

@app.get("/brands")
async def get_brands(condition: Optional[str] = None):
    """Get clean list of car brands"""
    if condition == "neuf":
        # Return clean brands from HTML carousel (no Occasion entries)
        brands = CLEAN_BRANDS
        logger.info(f"Returning {len(brands)} clean Neuf brands from HTML carousel")
        return {"brands": brands, "source": "clean_html_carousel", "count": len(brands)}
    
    elif condition == "occasion":
        # For occasion, return a subset
        occasion_brands = [brand for brand in CLEAN_BRANDS if brand in CLEAN_CAR_DATA.keys()]
        return {"brands": occasion_brands, "source": "clean_data", "count": len(occasion_brands)}
    
    else:
        # Return all clean brands
        all_brands = list(set(CLEAN_BRANDS + list(CLEAN_CAR_DATA.keys())))
        return {"brands": sorted(all_brands), "source": "combined_clean", "count": len(all_brands)}

@app.get("/brands/{brand}/models")
async def get_brand_models(brand: str):
    """Get models for a specific brand"""
    brand_upper = brand.upper()
    
    if brand_upper in CLEAN_CAR_DATA:
        models = list(CLEAN_CAR_DATA[brand_upper].keys())
        return {
            "brand": brand_upper,
            "models": sorted(models),
            "count": len(models),
            "source": "clean_data"
        }
    else:
        # Return empty if brand not found
        return {
            "brand": brand_upper,
            "models": [],
            "count": 0,
            "source": "not_found"
        }

@app.get("/brands/{brand}/models/{model}/listings")
async def get_model_listings(brand: str, model: str, limit: int = 10):
    """Get listings for a specific brand and model"""
    brand_upper = brand.upper()
    model_upper = model.upper()
    
    if brand_upper in CLEAN_CAR_DATA and model_upper in CLEAN_CAR_DATA[brand_upper]:
        listings = CLEAN_CAR_DATA[brand_upper][model_upper][:limit]
        return {
            "brand": brand_upper,
            "model": model_upper,
            "listings": listings,
            "count": len(listings),
            "total_available": len(CLEAN_CAR_DATA[brand_upper][model_upper]),
            "source": "clean_data"
        }
    else:
        return {
            "brand": brand_upper,
            "model": model_upper,
            "listings": [],
            "count": 0,
            "total_available": 0,
            "source": "not_found"
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
    """Debug endpoint showing data statistics"""
    stats = {
        "clean_brands_count": len(CLEAN_BRANDS),
        "clean_data_brands": len(CLEAN_CAR_DATA),
        "cache_size": len(cache),
        "ml_model_loaded": ml_model.is_loaded()
    }
    
    if CLEAN_CAR_DATA:
        stats["sample_brands"] = list(CLEAN_CAR_DATA.keys())[:5]
        stats["total_models"] = sum(len(models) for models in CLEAN_CAR_DATA.values())
        stats["total_listings"] = sum(
            len(listings) for brand_models in CLEAN_CAR_DATA.values() 
            for listings in brand_models.values()
        )
    
    return stats

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
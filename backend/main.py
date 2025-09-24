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
        
        # Generate ML prediction
        ml_prediction = ml_model.predict(request)
        
        # Create cache key for scraping results
        cache_key = f"{request.Brand.lower()}_{request.Model.lower()}_{request.Year}"
        
        # Check cache first
        if cache_key in listings_cache:
            logger.info(f"Using cached listings for {cache_key}")
            cached_data = listings_cache[cache_key]
            listings = cached_data['listings']
            market_avg = cached_data['market_avg']
            source = cached_data['source']
        else:
            # Scrape listings from Moroccan websites
            logger.info(f"Scraping listings for {request.Brand} {request.Model}")
            
            # Try Avito first, then Moteur.ma as fallback
            listings = []
            source = "none"
            
            try:
                avito_listings = await fetch_avito_listings(
                    request.Brand, request.Model, request.Year
                )
                if avito_listings:
                    listings = avito_listings
                    source = "avito.ma"
                    logger.info(f"Found {len(listings)} listings from Avito")
            except Exception as e:
                logger.warning(f"Avito scraping failed: {str(e)}")
            
            # Fallback to Moteur.ma if Avito failed or returned no results
            if not listings:
                try:
                    moteur_listings = await fetch_moteur_listings(
                        request.Brand, request.Model, request.Year
                    )
                    if moteur_listings:
                        listings = moteur_listings
                        source = "moteur.ma"
                        logger.info(f"Found {len(listings)} listings from Moteur")
                except Exception as e:
                    logger.warning(f"Moteur scraping failed: {str(e)}")
            
            # Compute market average
            market_avg = compute_average_price(listings) if listings else None
            
            # Cache the results
            listings_cache[cache_key] = {
                'listings': listings,
                'market_avg': market_avg,
                'source': source
            }
        
        # Prepare response
        car_listings = []
        for listing in listings[:3]:  # Top 3 listings
            car_listings.append(CarListing(
                title=listing['title'],
                price=listing['price'],
                url=listing['url']
            ))
        
        response = PredictionResponse(
            predicted_price=int(ml_prediction['price']),
            currency="MAD",
            market_avg_price=market_avg,
            listings=car_listings,
            model_confidence=ml_prediction['confidence'],
            scraping_source=source
        )
        
        logger.info(f"Prediction completed: ML={int(ml_prediction['price'])}, Market={market_avg}, Source={source}")
        
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
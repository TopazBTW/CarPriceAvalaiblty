#!/usr/bin/env python3
"""
Used Cars Scraping API - FastAPI endpoints for real-time scraping
"""

import asyncio
import subprocess
import json
import os
import csv
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from models.ml_model import MLModel

app = FastAPI(title="Morocco Used Cars Scraper API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    max_price: Optional[int] = None
    city: Optional[str] = None
    source: str = "both"  # "avito", "facebook", or "both"

class UsedCar(BaseModel):
    brand: str
    model: str
    year: Optional[int]
    price: int
    mileage: int
    fuel_type: str
    transmission: str
    city: str
    url: str
    phone: Optional[str]
    description: str
    source: str
    images: Optional[List[str]] = []

class PredictionRequest(BaseModel):
    brand: str
    model: str
    year: int
    km_driven: int
    fuel_type: str
    transmission: str
    seller_type: Optional[str] = "Individual"
    owner: Optional[str] = "First Owner"

# Global storage for scraped results
scraped_results = []
scraping_status = {"status": "idle", "progress": 0, "message": ""}

# Global ML model and data storage
ml_model = None
brands_data = None
cars_data = None

# Load data on startup
def load_data():
    global brands_data, cars_data, ml_model
    try:
        # Load brands data
        with open("data/json/morocco_brands_clean.json", "r", encoding="utf-8") as f:
            brands_data = json.load(f)
        
        # Load cars data (includes models)
        with open("data/json/morocco_cars_clean.json", "r", encoding="utf-8") as f:
            cars_data = json.load(f)
            
        # Initialize ML model
        ml_model = MLModel()
        print("✅ Data and ML model loaded successfully")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        brands_data = {"brands": []}
        cars_data = {"brands": {}, "models": {}}

# Load data on import
load_data()

@app.get("/")
async def root():
    return {
        "message": "Morocco Used Cars Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "brands": "/brands",
            "models": "/brands/{brand}/models", 
            "predict": "/predict",
            "search": "/search",
            "search-cars": "/search-cars",
            "status": "/scraping-status",
            "results": "/scraped-results"
        }
    }

@app.get("/brands")
async def get_brands():
    """Get all available car brands"""
    if not brands_data:
        raise HTTPException(status_code=500, detail="Brands data not loaded")
    
    return {
        "brands": [brand["name"] for brand in brands_data.get("brands", [])]
    }

@app.get("/brands/{brand}/models")
async def get_models_for_brand(brand: str):
    """Get all models for a specific brand"""
    if not cars_data:
        raise HTTPException(status_code=500, detail="Cars data not loaded")
    
    brand_upper = brand.upper()
    brand_models = cars_data.get("models", {}).get(brand_upper, {})
    
    models = list(brand_models.keys())
    
    return {
        "models": [{"name": model} for model in models]
    }

@app.post("/predict")
async def predict_car_price(request: PredictionRequest):
    """Predict car price using ML model"""
    if not ml_model:
        raise HTTPException(status_code=500, detail="ML model not loaded")
    
    try:
        # Prepare data for prediction
        car_data = {
            "Brand": request.brand,
            "Model": request.model,
            "Year": request.year,
            "KM_Driven": request.km_driven,
            "Fuel": request.fuel_type,
            "Transmission": request.transmission,
            "Seller_Type": request.seller_type,
            "Owner": request.owner
        }
        
        # Make prediction
        result = ml_model.predict(car_data)
        
        return {
            "predicted_price": result["price"],
            "confidence": result["confidence"],
            "currency": "MAD",
            "model_info": {
                "rf_prediction": result.get("rf_prediction"),
                "gb_prediction": result.get("gb_prediction")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")

@app.get("/search")
async def search_cars_simple(brand: Optional[str] = None, model: Optional[str] = None, 
                           min_price: Optional[int] = None, max_price: Optional[int] = None):
    """Simple car search endpoint"""
    if not cars_data:
        raise HTTPException(status_code=500, detail="Cars data not loaded")
    
    results = []
    
    try:
        # Search through the cars data
        models_data = cars_data.get("models", {})
        
        for brand_name, brand_models in models_data.items():
            # Filter by brand if specified
            if brand and brand.upper() != brand_name.upper():
                continue
                
            for model_name, cars in brand_models.items():
                # Filter by model if specified
                if model and model.lower() not in model_name.lower():
                    continue
                    
                for car in cars[:5]:  # Limit to 5 cars per model
                    car_price = car.get("price", 0)
                    
                    # Filter by price range
                    if min_price and car_price < min_price:
                        continue
                    if max_price and car_price > max_price:
                        continue
                        
                    results.append({
                        "id": car.get("id"),
                        "brand": car.get("brand"),
                        "model": car.get("model"),
                        "price": car_price,
                        "year": car.get("year"),
                        "fuel_type": car.get("fuel_type"),
                        "transmission": car.get("transmission"),
                        "url": car.get("url"),
                        "image": car.get("image")
                    })
                    
        # Limit total results
        results = results[:20]
        
        return {
            "cars": results,
            "total": len(results),
            "search_criteria": {
                "brand": brand,
                "model": model,
                "min_price": min_price,
                "max_price": max_price
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Search error: {str(e)}")

@app.post("/search-cars")
async def search_cars(request: SearchRequest, background_tasks: BackgroundTasks):
    """
    Trigger scraping for specific car criteria
    """
    global scraping_status
    
    if scraping_status["status"] == "running":
        raise HTTPException(status_code=400, detail="Scraping already in progress")
    
    # Clear previous results
    global scraped_results
    scraped_results = []
    
    # Start scraping in background
    background_tasks.add_task(run_scraping, request)
    
    scraping_status = {
        "status": "started",
        "progress": 0,
        "message": f"Starting search for {request.brand} {request.model}".strip()
    }
    
    return {
        "message": "Scraping started",
        "search_criteria": request.dict(),
        "estimated_time": "2-5 minutes"
    }

@app.get("/scraping-status")
async def get_scraping_status():
    """
    Get current scraping status
    """
    return scraping_status

@app.get("/scraped-results")
async def get_scraped_results():
    """
    Get latest scraped results
    """
    return {
        "total_cars": len(scraped_results),
        "cars": scraped_results,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/quick-search/{brand}")
async def quick_search(brand: str, background_tasks: BackgroundTasks):
    """
    Quick search for a specific brand
    """
    request = SearchRequest(brand=brand, source="both")
    return await search_cars(request, background_tasks)

@app.get("/quick-search/{brand}/{model}")
async def quick_search_with_model(brand: str, model: str, background_tasks: BackgroundTasks):
    """
    Quick search for specific brand and model
    """
    request = SearchRequest(brand=brand, model=model, source="both")
    return await search_cars(request, background_tasks)

async def run_scraping(request: SearchRequest):
    """
    Run the actual scraping process
    """
    global scraping_status, scraped_results
    
    scraping_status = {
        "status": "running",
        "progress": 10,
        "message": "Initializing scrapers..."
    }
    
    try:
        # Build scrapy command arguments
        base_args = []
        if request.brand:
            base_args.extend(["-a", f"brand={request.brand}"])
        if request.model:
            base_args.extend(["-a", f"model={request.model}"])
        if request.max_price:
            base_args.extend(["-a", f"max_price={request.max_price}"])
        if request.city:
            base_args.extend(["-a", f"city={request.city}"])
        
        scraped_items = []
        
        # Run Avito spider
        if request.source in ["avito", "both"]:
            scraping_status["message"] = "Scraping Avito..."
            scraping_status["progress"] = 25
            
            avito_results = await run_spider("avito", base_args)
            scraped_items.extend(avito_results)
            
        # Run Facebook spider  
        if request.source in ["facebook", "both"]:
            scraping_status["message"] = "Scraping Facebook Marketplace..."
            scraping_status["progress"] = 60
            
            facebook_results = await run_spider("facebook_marketplace", base_args)
            scraped_items.extend(facebook_results)
        
        # Process and clean results
        scraping_status["message"] = "Processing results..."
        scraping_status["progress"] = 85
        
        scraped_results = process_scraped_data(scraped_items)
        
        # Complete
        scraping_status = {
            "status": "completed",
            "progress": 100,
            "message": f"Found {len(scraped_results)} cars"
        }
        
    except Exception as e:
        scraping_status = {
            "status": "error",
            "progress": 0,
            "message": f"Error: {str(e)}"
        }

async def run_spider(spider_name: str, args: List[str]) -> List[Dict]:
    """
    Run a specific scrapy spider and return results
    """
    try:
        # Change to scrapy project directory
        scrapy_dir = Path(__file__).parent / "scrapy_project"
        
        # Build scrapy command
        cmd = ["scrapy", "crawl", spider_name] + args + ["-o", f"temp_{spider_name}.json"]
        
        # Run scrapy as subprocess
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(scrapy_dir),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        # Read results from temporary JSON file
        temp_file = scrapy_dir / f"temp_{spider_name}.json"
        results = []
        
        if temp_file.exists():
            try:
                with open(temp_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                temp_file.unlink()  # Delete temp file
            except json.JSONDecodeError:
                # Try reading as JSONL (line-by-line JSON)
                with open(temp_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            try:
                                results.append(json.loads(line))
                            except json.JSONDecodeError:
                                continue
                temp_file.unlink()
        
        return results
        
    except Exception as e:
        print(f"Error running spider {spider_name}: {e}")
        return []

def process_scraped_data(raw_items: List[Dict]) -> List[Dict]:
    """
    Clean and process scraped data
    """
    processed_items = []
    
    for item in raw_items:
        # Basic validation
        if not item.get('price') or item.get('price') < 10000:
            continue
            
        if not item.get('brand') or not item.get('model'):
            continue
            
        # Clean and structure data
        cleaned_item = {
            'brand': str(item.get('brand', '')).upper().strip(),
            'model': str(item.get('model', '')).upper().strip(), 
            'year': item.get('year'),
            'price': int(item.get('price', 0)),
            'mileage': int(item.get('mileage', 0)),
            'fuel_type': str(item.get('fuel_type', 'ESSENCE')).upper(),
            'transmission': str(item.get('transmission', 'MANUELLE')).upper(),
            'city': str(item.get('city', '')).title(),
            'url': str(item.get('url', '')),
            'phone': item.get('phone'),
            'description': str(item.get('description', ''))[:200],  # Limit description length
            'source': str(item.get('source', '')),
            'images': item.get('images', [])[:3] if item.get('images') else []
        }
        
        processed_items.append(cleaned_item)
    
    # Remove duplicates based on URL
    seen_urls = set()
    unique_items = []
    
    for item in processed_items:
        if item['url'] not in seen_urls:
            seen_urls.add(item['url'])
            unique_items.append(item)
    
    # Sort by price (ascending)
    unique_items.sort(key=lambda x: x['price'])
    
    return unique_items

@app.get("/test-scrapers")
async def test_scrapers():
    """
    Test endpoint to verify scrapers are working
    """
    try:
        # Test with a simple BMW search
        request = SearchRequest(brand="BMW", source="avito")
        
        global scraped_results, scraping_status
        scraped_results = []
        scraping_status = {"status": "testing", "progress": 0, "message": "Testing scrapers..."}
        
        # Run a quick test
        avito_results = await run_spider("avito", ["-a", "brand=BMW"])
        
        return {
            "status": "success",
            "avito_results": len(avito_results),
            "sample_data": avito_results[:2] if avito_results else [],
            "message": "Scrapers are working"
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e),
            "suggestion": "Make sure Scrapy is installed: pip install scrapy"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
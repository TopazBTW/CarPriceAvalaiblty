#!/usr/bin/env python3
"""
🚗 MOROCCO CAR VALUATION API - UPDATED WITH REAL KIFAL.MA DATA
FastAPI backend with accurate car data from neuf.kifal.ma
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Morocco Car Valuation API",
    description="Car valuation system with real data from Kifal.ma",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data storage
car_data: Dict[str, Any] = {}
brands_data: Dict[str, Any] = {}

def load_car_data():
    """Load complete car data from generated dataset"""
    global car_data, brands_data
    
    try:
        # Load main car data (new structure)
        cars_file = Path("data/json/morocco_cars_clean.json")
        if cars_file.exists():
            with open(cars_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                car_data = data
                brands_data = data.get('brands', {})
                
                # Count total cars from models
                total_cars = 0
                for brand_models in data.get('models', {}).values():
                    for model_cars in brand_models.values():
                        total_cars += len(model_cars)
                
                logger.info(f"✅ Loaded {total_cars} cars from complete dataset")
                logger.info(f"✅ Loaded {len(brands_data)} brands")
        
        if not car_data:
            logger.warning("⚠️ No data found - generating sample data")
            car_data = {"brands": {}, "models": {}, "metadata": {}}
            brands_data = {}
            
    except Exception as e:
        logger.error(f"❌ Error loading data: {e}")
        car_data = {"brands": {}, "models": {}, "metadata": {}}
        brands_data = {}

# Pydantic models
class CarPredictionRequest(BaseModel):
    brand: str
    model: str
    year: int
    mileage: int = 0
    condition: str = "Excellent"

class CarPredictionResponse(BaseModel):
    predicted_price: int
    confidence: float
    price_range: str
    market_data: Dict[str, Any]

class BrandInfo(BaseModel):
    name: str
    category: str
    total_models: int
    price_range: str
    image_url: Optional[str] = None

class SearchFilters(BaseModel):
    brand: Optional[str] = None
    price_min: Optional[int] = None
    price_max: Optional[int] = None
    year_min: Optional[int] = None
    year_max: Optional[int] = None
    fuel_type: Optional[str] = None

# API Endpoints

@app.on_event("startup")
async def startup_event():
    """Load data on startup"""
    load_car_data()

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Morocco Car Valuation API",
        "version": "2.0.0",
        "data_source": "kifal.ma",
        "documentation": "/docs",
        "total_cars": len(car_data.get('cars', [])),
        "total_brands": len(car_data.get('brands', {})),
        "last_updated": car_data.get('metadata', {}).get('processed_at')
    }

@app.get("/brands")
async def get_brands():
    """Get all available car brands"""
    try:
        if not brands_data.get('brands'):
            return {"brands": [], "message": "No brands data available"}
        
        # Add model count to each brand
        enriched_brands = []
        for brand in brands_data['brands']:
            brand_name = brand['name']
            model_count = len(car_data.get('models', {}).get(brand_name, {}))
            
            # Calculate price range for brand
            brand_cars = [car for car in car_data.get('cars', []) if car['brand'] == brand_name]
            prices = [car['price'] for car in brand_cars if car.get('price')]
            
            price_range = "Prix non disponible"
            if prices:
                min_price = min(prices)
                max_price = max(prices)
                price_range = f"{min_price:,} - {max_price:,} MAD"
            
            enriched_brands.append({
                **brand,
                'total_models': model_count,
                'price_range': price_range,
                'total_cars': len(brand_cars)
            })
        
        return {
            "brands": enriched_brands,
            "categories": brands_data.get('categories', {}),
            "total": len(enriched_brands)
        }
        
    except Exception as e:
        logger.error(f"Error getting brands: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving brands data")

@app.get("/brands/{brand_name}/models")
async def get_brand_models(brand_name: str):
    """Get all models for a specific brand"""
    try:
        brand_name_upper = brand_name.upper()
        models = car_data.get('models', {}).get(brand_name_upper, {})
        
        if not models:
            return {"models": [], "message": f"No models found for brand {brand_name}"}
        
        # Enrich models with additional data
        enriched_models = []
        for model_name, model_cars in models.items():
            prices = [car['price'] for car in model_cars if car.get('price')]
            
            price_range = "Prix non disponible"
            if prices:
                min_price = min(prices)
                max_price = max(prices)
                price_range = f"{min_price:,} - {max_price:,} MAD"
            
            # Get most recent car data
            latest_car = max(model_cars, key=lambda x: x.get('year', 0) or 0)
            
            enriched_models.append({
                'name': model_name,
                'brand': brand_name_upper,
                'total_variations': len(model_cars),
                'price_range': price_range,
                'years_available': list(set(car.get('year') for car in model_cars if car.get('year'))),
                'fuel_types': list(set(car.get('fuel_type') for car in model_cars if car.get('fuel_type'))),
                'image': latest_car.get('image'),
                'url': latest_car.get('url')
            })
        
        return {
            "brand": brand_name_upper,
            "models": enriched_models,
            "total": len(enriched_models)
        }
        
    except Exception as e:
        logger.error(f"Error getting models for {brand_name}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving models data")

@app.post("/predict")
async def predict_price(request: CarPredictionRequest):
    """Predict car price using market data"""
    try:
        brand_name = request.brand.upper()
        model_name = request.model
        
        # Find matching cars in dataset
        matching_cars = []
        for car in car_data.get('cars', []):
            if (car['brand'] == brand_name and 
                car['model'].lower() == model_name.lower()):
                matching_cars.append(car)
        
        if not matching_cars:
            # Fallback: try to find similar models
            similar_cars = [car for car in car_data.get('cars', []) 
                          if car['brand'] == brand_name]
            
            if similar_cars:
                avg_price = sum(car['price'] for car in similar_cars if car.get('price')) // len(similar_cars)
                return CarPredictionResponse(
                    predicted_price=avg_price,
                    confidence=0.4,  # Low confidence for brand average
                    price_range=f"{avg_price-50000:,} - {avg_price+50000:,} MAD",
                    market_data={
                        "method": "brand_average",
                        "similar_cars_found": len(similar_cars),
                        "message": f"No exact model match, using {brand_name} brand average"
                    }
                )
            else:
                raise HTTPException(status_code=404, detail=f"No data found for brand {brand_name}")
        
        # Calculate price based on matching cars
        prices = [car['price'] for car in matching_cars if car.get('price')]
        
        if not prices:
            raise HTTPException(status_code=404, detail="No pricing data available for this model")
        
        # Calculate average price
        base_price = sum(prices) // len(prices)
        
        # Adjust for year (depreciation)
        current_year = 2024
        year_adjustment = (request.year - current_year) * 0.15  # 15% per year
        
        # Adjust for mileage (if provided)
        mileage_adjustment = -min(request.mileage * 0.5, base_price * 0.3)  # Max 30% reduction
        
        # Adjust for condition
        condition_multipliers = {
            "Excellent": 1.0,
            "Très bon": 0.95,
            "Bon": 0.85,
            "Correct": 0.75,
            "Médiocre": 0.60
        }
        condition_multiplier = condition_multipliers.get(request.condition, 0.85)
        
        # Final price calculation
        predicted_price = int(base_price * (1 + year_adjustment) + mileage_adjustment) * condition_multiplier
        predicted_price = max(predicted_price, base_price * 0.4)  # Minimum 40% of base price
        
        # Calculate confidence based on data availability
        confidence = min(0.9, 0.5 + (len(matching_cars) * 0.1))
        
        return CarPredictionResponse(
            predicted_price=int(predicted_price),
            confidence=round(confidence, 2),
            price_range=f"{int(predicted_price*0.9):,} - {int(predicted_price*1.1):,} MAD",
            market_data={
                "method": "market_analysis",
                "matching_cars": len(matching_cars),
                "base_price": base_price,
                "year_adjustment": f"{year_adjustment*100:+.1f}%",
                "condition_multiplier": condition_multiplier,
                "mileage_impact": int(mileage_adjustment),
                "data_source": "kifal.ma"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error predicting price: {e}")
        raise HTTPException(status_code=500, detail="Error calculating price prediction")

@app.get("/search")
async def search_cars(
    q: Optional[str] = Query(None, description="Search query"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    price_min: Optional[int] = Query(None, description="Minimum price"),
    price_max: Optional[int] = Query(None, description="Maximum price"),
    year_min: Optional[int] = Query(None, description="Minimum year"),
    year_max: Optional[int] = Query(None, description="Maximum year"),
    fuel_type: Optional[str] = Query(None, description="Fuel type"),
    limit: int = Query(50, description="Maximum results to return")
):
    """Search cars with filters"""
    try:
        results = car_data.get('cars', [])
        
        # Apply filters
        if brand:
            results = [car for car in results if car['brand'].upper() == brand.upper()]
        
        if q:
            query_lower = q.lower()
            results = [car for car in results if 
                      query_lower in car['brand'].lower() or 
                      query_lower in car['model'].lower()]
        
        if price_min:
            results = [car for car in results if car.get('price', 0) >= price_min]
        
        if price_max:
            results = [car for car in results if car.get('price', 0) <= price_max]
        
        if year_min:
            results = [car for car in results if (car.get('year') or 0) >= year_min]
        
        if year_max:
            results = [car for car in results if (car.get('year') or 0) <= year_max]
        
        if fuel_type:
            results = [car for car in results if 
                      car.get('fuel_type', '').upper() == fuel_type.upper()]
        
        # Limit results
        results = results[:limit]
        
        return {
            "cars": results,
            "total": len(results),
            "filters_applied": {
                "query": q,
                "brand": brand,
                "price_range": f"{price_min or 'Any'} - {price_max or 'Any'}",
                "year_range": f"{year_min or 'Any'} - {year_max or 'Any'}",
                "fuel_type": fuel_type
            }
        }
        
    except Exception as e:
        logger.error(f"Error searching cars: {e}")
        raise HTTPException(status_code=500, detail="Error performing search")

@app.get("/statistics")
async def get_statistics():
    """Get market statistics"""
    try:
        cars = car_data.get('cars', [])
        
        if not cars:
            return {"message": "No statistics available", "cars_analyzed": 0}
        
        # Price statistics
        prices = [car['price'] for car in cars if car.get('price')]
        price_stats = {}
        if prices:
            price_stats = {
                "min": min(prices),
                "max": max(prices),
                "average": sum(prices) // len(prices),
                "median": sorted(prices)[len(prices)//2]
            }
        
        # Brand distribution
        brand_counts = {}
        for car in cars:
            brand = car.get('brand', 'Unknown')
            brand_counts[brand] = brand_counts.get(brand, 0) + 1
        
        # Year distribution
        year_counts = {}
        for car in cars:
            year = car.get('year')
            if year:
                year_counts[year] = year_counts.get(year, 0) + 1
        
        return {
            "total_cars": len(cars),
            "total_brands": len(car_data.get('brands', {})),
            "price_statistics": price_stats,
            "brand_distribution": dict(sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "year_distribution": dict(sorted(year_counts.items(), reverse=True)[:10]),
            "price_ranges": car_data.get('metadata', {}).get('price_ranges', {}),
            "data_source": "kifal.ma",
            "last_updated": car_data.get('metadata', {}).get('processed_at')
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving statistics")

if __name__ == "__main__":
    print("🚗 MOROCCO CAR VALUATION API")
    print("=" * 35)
    print("📊 Data Source: Kifal.ma")
    print("🌐 Server: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
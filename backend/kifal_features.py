#!/usr/bin/env python3
"""
🚗 KIFAL-STYLE FEATURES FOR MOROCCO CAR VALUATION
Advanced search, filtering, and car recommendations similar to Kifal.ma
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
from pathlib import Path

# Car body types like Kifal.ma
CAR_BODY_TYPES = [
    "Berline",
    "Cabriolet / Roadster", 
    "Citadine",
    "Compacte",
    "Coupé", 
    "Crossover",
    "Fourgon / Cabine",
    "Ludospace / Utilitaire léger",
    "Microcitadine",
    "Minibus", 
    "Monospace / Break",
    "Pick-up",
    "SUV"
]

# Price ranges like Kifal.ma (in MAD)
PRICE_RANGES = [
    {"label": "moins de 200K DH", "min": 0, "max": 200000},
    {"label": "200K - 300K DH", "min": 200000, "max": 300000}, 
    {"label": "300K - 400K DH", "min": 300000, "max": 400000},
    {"label": "400K - 600K DH", "min": 400000, "max": 600000},
    {"label": "600K - 800K DH", "min": 600000, "max": 800000},
    {"label": "Plus de 800K DH", "min": 800000, "max": 999999999}
]

# Brand categories like Kifal.ma
BRAND_CATEGORIES = {
    "premium": [
        "BMW", "AUDI", "PORSCHE", "JEEP", "MINI", "VOLVO", 
        "LEXUS", "MASERATI", "CUPRA", "DS", "MERCEDES-BENZ", 
        "JAGUAR", "LAND ROVER", "ALFA ROMEO"
    ],
    "generaliste": [
        "KIA", "HYUNDAI", "VOLKSWAGEN", "TOYOTA", "DACIA", 
        "FORD", "PEUGEOT", "CITROEN", "SKODA", "FIAT", 
        "RENAULT", "NISSAN", "MAZDA", "HONDA"
    ],
    "electric": [
        "BYD", "ZEEKR"
    ],
    "chinese": [
        "CHANGAN", "CHERY", "BAIC", "DFSK", "GEELY", 
        "GWM", "JAECOO", "OMODA"
    ]
}

class CarSearchRequest(BaseModel):
    marque: Optional[str] = None
    modele: Optional[str] = None
    type: Optional[str] = None  # Body type
    min_prix: Optional[int] = None
    max_prix: Optional[int] = None
    carburant: Optional[str] = None
    transmission: Optional[str] = None

class CarRecommendation(BaseModel):
    brand: str
    model: str
    category: str
    price_range: str
    recommendation_type: str  # "Meilleur SUV", "Meilleur Citadine", etc.
    price: int
    url: str

class KifalStyleService:
    """Service to provide Kifal.ma style features"""
    
    def __init__(self, data_path: str = "data/json/car_data_clean_final.json"):
        self.data_path = data_path
        self.car_data = self.load_car_data()
    
    def load_car_data(self) -> Dict[str, Any]:
        """Load clean car data"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def get_brands_by_category(self, category: str = None) -> Dict[str, List[str]]:
        """Get brands organized by category like Kifal.ma"""
        if category and category in BRAND_CATEGORIES:
            available_brands = [b for b in BRAND_CATEGORIES[category] if b in self.car_data]
            return {category: available_brands}
        
        # Return all categories with available brands
        result = {}
        for cat, brands in BRAND_CATEGORIES.items():
            available_brands = [b for b in brands if b in self.car_data]
            if available_brands:
                result[cat] = available_brands
        
        return result
    
    def get_cars_by_price_range(self, min_price: int, max_price: int, limit: int = 20) -> List[Dict]:
        """Get cars in specific price range like Kifal.ma"""
        cars_in_range = []
        
        for brand, models in self.car_data.items():
            for model, listings in models.items():
                for listing in listings:
                    price = listing.get('price', 0)
                    if min_price <= price <= max_price:
                        cars_in_range.append({
                            "brand": brand,
                            "model": model, 
                            "title": listing.get('title', f"{brand} {model}"),
                            "price": price,
                            "url": listing.get('url', ''),
                            "year": listing.get('year')
                        })
        
        # Sort by price and limit results
        cars_in_range.sort(key=lambda x: x['price'])
        return cars_in_range[:limit]
    
    def get_best_recommendations(self) -> List[CarRecommendation]:
        """Generate best car recommendations by category like Kifal.ma"""
        recommendations = []
        
        # Best recommendations per price range
        price_range_recommendations = [
            {"range": "moins de 200K DH", "suv": "DACIA DUSTER", "citadine": "RENAULT CLIO"},
            {"range": "200K - 300K DH", "berline": "SKODA OCTAVIA", "hybrid": "TOYOTA YARIS CROSS"},
            {"range": "300K - 400K DH", "hybrid": "TOYOTA C-HR", "compacte": "VOLKSWAGEN GOLF"},
            {"range": "400K - 600K DH", "suv": "AUDI Q5", "coupe": "BMW SÉRIE 4"},
            {"range": "600K - 800K DH", "suv": "PORSCHE MACAN", "cabriolet": "MERCEDES-BENZ CLASSE E"},
            {"range": "Plus de 800K DH", "berline": "MERCEDES-BENZ CLASSE S", "suv": "LAMBORGHINI URUS"}
        ]
        
        for rec in price_range_recommendations:
            range_label = rec["range"]
            for category, model in rec.items():
                if category != "range":
                    # Try to find actual car data
                    brand, model_name = model.split(" ", 1) if " " in model else (model, "")
                    
                    if brand in self.car_data and model_name in self.car_data[brand]:
                        listings = self.car_data[brand][model_name]
                        if listings:
                            price = listings[0].get('price', 0)
                            recommendations.append(CarRecommendation(
                                brand=brand,
                                model=model_name,
                                category=category.capitalize(),
                                price_range=range_label,
                                recommendation_type=f"Meilleur {category.capitalize()}",
                                price=price,
                                url=f"/search?marque={brand}&modele={model_name}"
                            ))
        
        return recommendations
    
    def search_cars(self, search_params: CarSearchRequest) -> List[Dict]:
        """Advanced car search like Kifal.ma"""
        results = []
        
        for brand, models in self.car_data.items():
            # Filter by brand
            if search_params.marque and search_params.marque.upper() != brand:
                continue
                
            for model, listings in models.items():
                # Filter by model
                if search_params.modele and search_params.modele.upper() not in model.upper():
                    continue
                
                for listing in listings:
                    price = listing.get('price', 0)
                    
                    # Filter by price range
                    if search_params.min_prix and price < search_params.min_prix:
                        continue
                    if search_params.max_prix and price > search_params.max_prix:
                        continue
                    
                    # Add to results
                    results.append({
                        "brand": brand,
                        "model": model,
                        "title": listing.get('title', f"{brand} {model}"),
                        "price": price,
                        "url": listing.get('url', ''),
                        "year": listing.get('year'),
                        "image": f"https://referentiel.kifal.ma/imgs/brands/{brand}.webp"  # Like Kifal.ma
                    })
        
        return sorted(results, key=lambda x: x['price'])
    
    def get_popular_models(self, limit: int = 10) -> List[Dict]:
        """Get popular/top models like Kifal.ma"""
        model_popularity = {}
        
        for brand, models in self.car_data.items():
            for model, listings in models.items():
                key = f"{brand} {model}"
                model_popularity[key] = {
                    "brand": brand,
                    "model": model, 
                    "listing_count": len(listings),
                    "avg_price": sum(l.get('price', 0) for l in listings) // len(listings) if listings else 0
                }
        
        # Sort by popularity (number of listings)
        popular = sorted(model_popularity.values(), 
                        key=lambda x: x['listing_count'], reverse=True)
        
        return popular[:limit]

# FastAPI endpoints for Kifal.ma style features
def add_kifal_endpoints(app: FastAPI):
    """Add Kifal.ma style endpoints to FastAPI app"""
    
    kifal_service = KifalStyleService()
    
    @app.get("/kifal/brands")
    async def get_brands_by_category(category: Optional[str] = None):
        """Get brands organized by category (premium, generaliste, etc.)"""
        return kifal_service.get_brands_by_category(category)
    
    @app.get("/kifal/price-ranges")
    async def get_price_ranges():
        """Get available price ranges like Kifal.ma"""
        return PRICE_RANGES
    
    @app.get("/kifal/body-types")
    async def get_body_types():
        """Get available car body types"""
        return CAR_BODY_TYPES
    
    @app.get("/kifal/search")
    async def advanced_search(
        marque: Optional[str] = None,
        modele: Optional[str] = None,
        type: Optional[str] = None,
        min_prix: Optional[int] = None,
        max_prix: Optional[int] = None,
        limit: int = Query(20, le=100)
    ):
        """Advanced car search like Kifal.ma"""
        search_params = CarSearchRequest(
            marque=marque,
            modele=modele, 
            type=type,
            min_prix=min_prix,
            max_prix=max_prix
        )
        
        results = kifal_service.search_cars(search_params)
        return {
            "results": results[:limit],
            "total": len(results),
            "filters_applied": {
                "marque": marque,
                "modele": modele,
                "type": type,
                "price_range": f"{min_prix or 0} - {max_prix or 'MAX'} DH"
            }
        }
    
    @app.get("/kifal/price-range/{range_label}")
    async def get_cars_by_price_range(range_label: str):
        """Get cars by price range like Kifal.ma categories"""
        # Find matching price range
        price_range = None
        for pr in PRICE_RANGES:
            if pr["label"] == range_label:
                price_range = pr
                break
        
        if not price_range:
            raise HTTPException(status_code=404, detail="Price range not found")
        
        cars = kifal_service.get_cars_by_price_range(
            price_range["min"], price_range["max"]
        )
        
        return {
            "price_range": range_label,
            "cars": cars,
            "count": len(cars)
        }
    
    @app.get("/kifal/recommendations")
    async def get_recommendations():
        """Get best car recommendations by category"""
        return kifal_service.get_best_recommendations()
    
    @app.get("/kifal/popular")
    async def get_popular_models():
        """Get popular/top models"""
        return kifal_service.get_popular_models()

if __name__ == "__main__":
    # Test the service
    service = KifalStyleService()
    
    print("🚗 TESTING KIFAL.MA STYLE FEATURES")
    print("=" * 40)
    
    # Test brand categories
    brands = service.get_brands_by_category()
    print(f"Brand categories: {len(brands)}")
    for cat, brand_list in brands.items():
        print(f"  {cat}: {len(brand_list)} brands")
    
    # Test price range search
    cars_200k = service.get_cars_by_price_range(0, 200000, 5)
    print(f"\\nCars under 200K DH: {len(cars_200k)}")
    
    # Test recommendations
    recommendations = service.get_best_recommendations()
    print(f"\\nRecommendations: {len(recommendations)}")
    
    print("\\n🎉 Kifal.ma style features ready!")
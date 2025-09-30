from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
import aiohttp
import os
import re
from urllib.parse import quote, urljoin
from pathlib import Path
from bs4 import BeautifulSoup
from cachetools import TTLCache

from ml_model import MLModel
from real_morocco_prices import get_real_morocco_price, MOROCCO_REAL_PRICES
from wandaloo_scraper import (
    fetch_wandaloo_new_versions, 
    fetch_wandaloo_brands,
    fetch_wandaloo_models, 
    fetch_wandaloo_model_listings
)
from scrapers import fetch_avito_listings, fetch_moteur_listings, compute_average_price
from production_scraper import get_production_morocco_prices

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
                logger.info("No real market data found, trying production scraper...")
                
                try:
                    # Utiliser le scraper de production
                    market_data = await get_production_morocco_prices(
                        request.Brand, request.Model, request.Year, vehicle_condition
                    )
                    
                    # Cache les résultats pour 30 minutes
                    listings_cache[cache_key] = market_data
                    logger.info(f"Production scraper completed: {market_data['data_points']} listings")
                    
                except Exception as e:
                    logger.warning(f"Production scraper failed: {str(e)}")
                    
                    # Final fallback to basic scrapers
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
                        
                    except Exception as e2:
                        logger.error(f"All scraping methods failed: {e2}")
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

        # If the vehicle is new (Neuf) and we have an official market price, prefer it entirely
        if vehicle_condition == "Neuf" and market_data.get('market_price'):
            # Use the official/new market price as the final prediction
            final_prediction = int(market_data['market_price'])

            # Prepare response using market data and return early
            car_listings = []
            sample_listings = market_data.get('sample_listings', [])
            for listing in sample_listings[:3]:
                if isinstance(listing, dict) and 'title' in listing:
                    car_listings.append(CarListing(
                        title=listing['title'],
                        price=listing['price'],
                        url=listing.get('url', f"https://www.google.com/search?q={request.Brand}+{request.Model}+neuf+maroc")
                    ))

            overall_confidence = 0.95

            response = PredictionResponse(
                predicted_price=final_prediction,
                currency="MAD",
                market_avg_price=market_data.get('market_price'),
                listings=car_listings,
                model_confidence=overall_confidence,
                scraping_source='morocco_real_prices'
            )

            logger.info(f"Neuf flow: returning official market price {final_prediction} for {request.Brand} {request.Model}")
            return response
        
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
async def list_brands(condition: Optional[str] = 'both'):
    """Return clean brand list extracted from wandaloo_marques.html footer carousel"""
    try:
        cache_key = f'clean_html_brands_{condition.lower()}'
        cached = listings_cache.get(cache_key)
        if cached:
            return {"brands": cached}

        # Read local saved marques HTML and extract from clean footer carousel
        marques_path = Path(__file__).parent / 'wandaloo_marques.html'
        if not marques_path.exists():
            logger.warning("wandaloo_marques.html not found, falling back to scraper")
            # Fallback to scraper
            try:
                mode = 'neuf' if condition and condition.lower() in ['neuf', 'new'] else 'both'
                brands = await fetch_wandaloo_brands(mode=mode) or []
                if mode == 'neuf':
                    brands = [b for b in brands if 'occasion' not in b.lower() and not re.search(r'\d', b)]
                listings_cache[cache_key] = brands
                return {"brands": brands}
            except Exception as e:
                logger.error(f"Scraper fallback failed: {e}")
                return {"brands": []}

        html = marques_path.read_text(encoding='utf-8', errors='ignore')
        soup = BeautifulSoup(html, 'html.parser')

        # Extract brands from footer carousel - these are guaranteed clean /neuf/ links
        carousel_items = soup.select('div.owl-carousel div.item a[href*="/neuf/"]')
        brands = []
        
        for item in carousel_items:
            href = item.get('href', '')
            if not href or '/neuf/' not in href:
                continue
                
            # Get brand name from img alt
            brand_name = ''
            img = item.find('img')
            if img and img.get('alt'):
                brand_name = img.get('alt').strip()
                # Clean up: remove year and "Neuve Maroc" suffix
                brand_name = re.sub(r'\b20\d{2}\b', '', brand_name)
                brand_name = re.sub(r'neuve|maroc', '', brand_name, flags=re.I).strip()
                brand_name = re.sub(r'[^A-Za-z0-9 \-]', ' ', brand_name).strip()
                brand_name = re.sub(r'\s+', ' ', brand_name)
            
            if not brand_name:
                # Fallback: extract from URL slug
                brand_slug = href.split('/neuf/')[-1].strip('/')
                brand_name = brand_slug.replace('-', ' ').title()
            
            if brand_name and brand_name not in brands:
                brands.append(brand_name)

        listings_cache[cache_key] = brands
        logger.info(f"Extracted {len(brands)} clean brands from HTML footer carousel")
        return {"brands": brands}

    except Exception as e:
        logger.error(f"Error listing brands: {e}")
        raise HTTPException(status_code=500, detail="Unable to list brands")


@app.get('/scrape/wandaloo/comprehensive_brands_and_models')
async def scrape_wandaloo_comprehensive_brands_and_models(limit: Optional[int] = 0):
    """Parse the saved wandaloo_marques.html for clean /neuf brand links from footer carousel,
    then for each brand scrape available models with prices, images, and links.
    
    Returns comprehensive data structure: {brand: {models: [{name, price_range, image, url}]}}
    Query params:
      - limit: max number of brands to process (0 = all)
    """
    try:
        cache_key = 'wandaloo_comprehensive_brands_models'
        cached = listings_cache.get(cache_key)
        if cached:
            return cached

        # Read local saved marques HTML 
        marques_path = Path(__file__).parent / 'wandaloo_marques.html'
        if not marques_path.exists():
            raise HTTPException(status_code=404, detail=f'{marques_path} not found')

        html = marques_path.read_text(encoding='utf-8', errors='ignore')
        soup = BeautifulSoup(html, 'html.parser')

        # Extract clean brand list from footer carousel (div.owl-carousel items)
        carousel_items = soup.select('div.owl-carousel div.item a[href*="/neuf/"]')
        clean_brands = []
        
        for item in carousel_items:
            href = item.get('href', '')
            if not href or '/neuf/' not in href:
                continue
                
            # Extract brand name from URL path (/neuf/brand-name/)
            brand_slug = href.split('/neuf/')[-1].strip('/')
            if not brand_slug:
                continue
                
            # Get clean brand name from img alt or title
            brand_name = ''
            img = item.find('img')
            if img and img.get('alt'):
                brand_name = img.get('alt').strip()
                # Clean up alt text (remove "2025 Neuve Maroc" etc)
                brand_name = re.sub(r'\b20\d{2}\b', '', brand_name)
                brand_name = re.sub(r'neuve|maroc', '', brand_name, flags=re.I).strip()
            
            if not brand_name:
                brand_name = item.get('title', '').strip()
                brand_name = re.sub(r'\b20\d{2}\b', '', brand_name)
                brand_name = re.sub(r'neuve|maroc', '', brand_name, flags=re.I).strip()
            
            if not brand_name:
                # Fallback: use slug but capitalize
                brand_name = brand_slug.replace('-', ' ').title()
                
            clean_brands.append({
                'name': brand_name,
                'slug': brand_slug,
                'url': href if href.startswith('http') else f'https://www.wandaloo.com{href}',
                'logo': img.get('src', '') if img else ''
            })
            
            if limit and len(clean_brands) >= limit:
                break

        logger.info(f"Extracted {len(clean_brands)} clean brands from HTML carousel")

        # For each brand, scrape models with details
        comprehensive_data = {}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        timeout = aiohttp.ClientTimeout(total=25)
        
        async def scrape_brand_models(session, brand_info):
            brand_name = brand_info['name']
            brand_url = brand_info['url']
            
            try:
                async with session.get(brand_url) as resp:
                    if resp.status != 200:
                        return brand_name, {'models': [], 'error': f'HTTP {resp.status}'}
                    
                    html = await resp.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    models = []
                    
                    # Look for model listings - common patterns on Wandaloo brand pages
                    model_selectors = [
                        'a[href*="/neuf/"][href*="' + brand_info['slug'] + '"]',
                        '.model-item a', 
                        '.voiture-item a',
                        '.listing a',
                        'article a'
                    ]
                    
                    found_models = set()
                    
                    for selector in model_selectors:
                        model_links = soup.select(selector)
                        for link in model_links:
                            href = link.get('href', '')
                            if not href or brand_info['slug'] not in href:
                                continue
                                
                            # Extract model name from link text or URL
                            model_name = link.get_text(strip=True)
                            if not model_name:
                                # Try to extract from URL
                                model_slug = href.split('/')[-2] if href.endswith('/') else href.split('/')[-1]
                                model_name = model_slug.replace('-', ' ').title()
                            
                            # Clean model name
                            model_name = re.sub(r'\b20\d{2}\b', '', model_name)
                            model_name = re.sub(r'neuve|maroc|prix', '', model_name, flags=re.I)
                            model_name = re.sub(r'[^A-Za-z0-9 \-]', ' ', model_name).strip()
                            model_name = re.sub(r'\s+', ' ', model_name)
                            
                            if len(model_name) < 2 or len(model_name) > 50:
                                continue
                                
                            if model_name.lower() in found_models:
                                continue
                            found_models.add(model_name.lower())
                            
                            # Try to extract price from surrounding context
                            parent_text = link.parent.get_text() if link.parent else ''
                            price_match = re.search(r'(\d[\d\s\.,]{2,})\s*(?:MAD|DH|dh)', parent_text, flags=re.I)
                            price = None
                            if price_match:
                                try:
                                    price = int(re.sub(r'[^0-9]', '', price_match.group(1)))
                                except:
                                    pass
                            
                            # Try to find model image
                            img_src = ''
                            nearby_img = link.find('img') or (link.parent.find('img') if link.parent else None)
                            if nearby_img and nearby_img.get('src'):
                                img_src = nearby_img.get('src')
                                if not img_src.startswith('http'):
                                    img_src = urljoin(brand_url, img_src)
                            
                            model_url = href if href.startswith('http') else urljoin('https://www.wandaloo.com', href)
                            
                            models.append({
                                'name': model_name,
                                'price': price,
                                'image': img_src,
                                'url': model_url
                            })
                            
                            if len(models) >= 20:  # Limit models per brand
                                break
                        
                        if models:  # If we found models with first selector, don't try others
                            break
                    
                    return brand_name, {'models': models, 'brand_logo': brand_info.get('logo', '')}
                    
            except Exception as e:
                logger.warning(f"Error scraping models for {brand_name}: {e}")
                return brand_name, {'models': [], 'error': str(e)}

        # Scrape models for all brands concurrently (with semaphore for rate limiting)
        sem = asyncio.Semaphore(4)  # Limit concurrent requests
        
        async def worker(session, brand_info):
            async with sem:
                return await scrape_brand_models(session, brand_info)

        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            tasks = [worker(session, brand) for brand in clean_brands]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, tuple):
                    brand_name, data = result
                    comprehensive_data[brand_name] = data
                else:
                    logger.error(f"Error in brand scraping task: {result}")

        # Cache results for 1 hour
        listings_cache[cache_key] = comprehensive_data
        logger.info(f"Comprehensive scraping completed for {len(comprehensive_data)} brands")
        
        return comprehensive_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in comprehensive brand/model scraping: {e}")
        raise HTTPException(status_code=500, detail="Comprehensive scraping failed")
async def scrape_wandaloo_brands_with_prices(limit: Optional[int] = 0):
    """Parse the saved `wandaloo_marques.html` file to extract /neuf brand links,
    then for each brand page attempt to fetch a representative price and an image.

    This is intentionally best-effort: it prefers meta og:image / first large image
    and price-like text containing MAD/DH. Results are cached for short TTL.
    Query params:
      - limit: max number of brands to process (0 = all)
    """
    try:
        cache_key = 'wandaloo_brands_with_prices'
        cached = listings_cache.get(cache_key)
        if cached:
            return cached

        # Read local saved marques HTML (provided in repo)
        marques_path = Path(__file__).parent / 'wandaloo_marques.html'
        if not marques_path.exists():
            raise HTTPException(status_code=404, detail=str(marques_path) + ' not found')

        html = marques_path.read_text(encoding='utf-8', errors='ignore')
        soup = BeautifulSoup(html, 'html.parser')

        # Find anchor links that point to /neuf/<slug>/ on wandaloo
        anchors = soup.find_all('a', href=True)
        brand_entries = []
        seen = set()
        for a in anchors:
            href = a.get('href') or ''
            if '/neuf/' not in href:
                continue
            # Only absolute wandaloo links or relative starting with /neuf/
            if href.startswith('http'):
                url = href
            else:
                url = urljoin('https://www.wandaloo.com', href)

            # Derive a name from img alt or anchor text
            name = ''
            img = a.find('img')
            if img and img.get('alt'):
                name = img.get('alt').strip()
            if not name:
                name = (a.get_text() or '').strip()
            if not name:
                # attempt title attribute
                name = (a.get('title') or '').strip()

            # normalize name
            name = re.sub(r"\b(202\d|202\d)\b", '', name)
            name = re.sub(r'neuve|maroc', '', name, flags=re.I).strip()
            name = re.sub(r'[^A-Za-z0-9 \-]', ' ', name).strip()
            name = re.sub(r'\s+', ' ', name)
            if not name:
                continue
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            brand_entries.append({'name': name.title(), 'url': url})
            if limit and limit > 0 and len(brand_entries) >= limit:
                break

        # Helper to fetch a brand page and extract a price + image
        async def fetch_brand_detail(session, entry):
            bname = entry['name']
            burl = entry['url']
            result = {'name': bname, 'url': burl, 'price': None, 'image': None}
            try:
                async with session.get(burl, timeout=15) as resp:
                    if resp.status != 200:
                        return result
                    text = await resp.text()
                    psoup = BeautifulSoup(text, 'html.parser')

                    # Try og:price:amount or meta price
                    meta_price = psoup.find('meta', attrs={'property': 'og:price:amount'}) or psoup.find('meta', attrs={'name': 'price'})
                    if meta_price and meta_price.get('content'):
                        try:
                            p = int(re.sub(r'[^0-9]', '', meta_price.get('content')))
                            result['price'] = p
                        except:
                            pass

                    # Search visible text for a price pattern (MAD/DH)
                    if not result['price']:
                        body_text = psoup.get_text(separator=' ', strip=True)
                        m = re.search(r"(\d[\d\s\.,]{2,})\s*(?:MAD|DH|Dh|dh)", body_text, flags=re.I)
                        if m:
                            try:
                                result['price'] = int(re.sub(r'[^0-9]', '', m.group(1)))
                            except:
                                pass

                    # Find representative image: og:image first, else largest img src
                    meta_img = psoup.find('meta', property='og:image') or psoup.find('meta', attrs={'name': 'og:image'})
                    if meta_img and meta_img.get('content'):
                        result['image'] = meta_img.get('content')
                    else:
                        # choose first img with reasonable dimensions or largest by filesize heuristic
                        imgs = psoup.find_all('img', src=True)
                        if imgs:
                            # prefer images with 'logo' in alt/src or those within header/hero
                            chosen = None
                            for im in imgs:
                                alt = (im.get('alt') or '').lower()
                                src = im.get('src')
                                if 'logo' in alt or 'logo' in src:
                                    chosen = src
                                    break
                            if not chosen:
                                chosen = imgs[0].get('src')
                            if chosen and not chosen.startswith('http'):
                                chosen = urljoin(burl, chosen)
                            result['image'] = chosen

            except Exception:
                pass
            return result

        # Fetch brand pages concurrently (bounded)
        results = []
        timeout = aiohttp.ClientTimeout(total=20)
        headers = {"User-Agent": "Mozilla/5.0 (compatible; PriceBot/1.0)"}
        sem = asyncio.Semaphore(6)

        async def worker(session, entry):
            async with sem:
                return await fetch_brand_detail(session, entry)

        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            tasks = [worker(session, e) for e in brand_entries]
            fetched = await asyncio.gather(*tasks)
            for f in fetched:
                results.append(f)

        listings_cache[cache_key] = results
        return {'brands': results}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scraping brands with prices: {e}")
        raise HTTPException(status_code=500, detail="Failed to scrape brands with prices")


@app.get('/brands/{brand}/models')
async def list_brand_models(brand: str):
    """Return models and available years for a given brand based on real Morocco DB"""
    try:
        # Prefer Wandaloo live models (new-focused)
        try:
            w_models = await fetch_wandaloo_models(brand)
            if w_models:
                models = [{'model': m, 'available_years': []} for m in w_models]
                return {"brand": brand, "models": models, 'source': 'wandaloo'}
        except Exception:
            logger.info(f"Wandaloo models fetch failed for brand {brand}")

        # Fallback: use internal DB but only include models that have a 'new' section
        brand_data = MOROCCO_REAL_PRICES.get(brand)
        if not brand_data:
            raise HTTPException(status_code=404, detail="Brand not found")

        models = []
        for model_name, model_data in brand_data.items():
            new_section = model_data.get('new', {})
            if not new_section:
                # Skip models that have only 'used' data — user requested new-only models
                continue
            years = sorted(list(new_section.keys()), reverse=True)
            models.append({
                'model': model_name,
                'available_years': years
            })

        return {"brand": brand, "models": models, 'source': 'internal_db_filtered'}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing models for {brand}: {e}")
        raise HTTPException(status_code=500, detail="Unable to list models")


@app.get('/brands/{brand}/models/{model}/new_versions')
async def list_new_versions(brand: str, model: str):
    """Return available new versions (year + price range) for brand/model from real DB"""
    try:
        brand_data = MOROCCO_REAL_PRICES.get(brand)
        if not brand_data:
            raise HTTPException(status_code=404, detail="Brand not found")

        model_data = brand_data.get(model)

        # First, try Wandaloo live aggregation of new versions
        try:
            versions = await fetch_wandaloo_new_versions(brand, model, max_results=8)
            if versions:
                return {'brand': brand, 'model': model, 'versions': versions, 'source': 'wandaloo'}
        except Exception:
            logger.info(f"Wandaloo scraping failed or returned empty for {brand} {model}")

        # Fallback to official DB data (only 'new' section)
        if not model_data:
            raise HTTPException(status_code=404, detail="Model not found")

        new_section = model_data.get('new', {})
        versions = []
        for year in sorted(new_section.keys(), reverse=True):
            yd = new_section[year]
            query = f"{brand} {model} {year} prix neuf maroc"
            url = f"https://www.google.com/search?q={quote(query)}"
            versions.append({
                'year': year,
                'min': yd.get('min'),
                'max': yd.get('max'),
                'url': url
            })

        return {'brand': brand, 'model': model, 'versions': versions, 'source': 'official_db'}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing new versions for {brand} {model}: {e}")
        raise HTTPException(status_code=500, detail="Unable to list new versions")
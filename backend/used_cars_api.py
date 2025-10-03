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

# Global storage for scraped results
scraped_results = []
scraping_status = {"status": "idle", "progress": 0, "message": ""}

@app.get("/")
async def root():
    return {
        "message": "Morocco Used Cars Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "search": "/search-cars",
            "status": "/scraping-status",
            "results": "/scraped-results"
        }
    }

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
#!/usr/bin/env python3
"""
Example integration showing how your frontend can call the scraping API
"""

import requests
import time
import json

# API base URL
API_BASE = "http://localhost:8001"

def search_used_cars(brand, model=None, max_price=None):
    """
    Example function your frontend can use to search for used cars
    """
    
    # Prepare search request
    search_data = {
        "brand": brand,
        "source": "both"  # Search both Avito and Facebook
    }
    
    if model:
        search_data["model"] = model
    if max_price:
        search_data["max_price"] = max_price
    
    print(f"🔍 Searching for: {brand} {model or ''}")
    
    try:
        # Start scraping
        response = requests.post(f"{API_BASE}/search-cars", json=search_data)
        
        if response.status_code == 200:
            print("✅ Scraping started successfully")
            
            # Monitor progress
            while True:
                status_response = requests.get(f"{API_BASE}/scraping-status")
                status = status_response.json()
                
                print(f"📊 Status: {status['status']} - {status['progress']}% - {status['message']}")
                
                if status['status'] == 'completed':
                    # Get results
                    results_response = requests.get(f"{API_BASE}/scraped-results")
                    results = results_response.json()
                    
                    print(f"\n🎉 Found {results['total_cars']} used cars!")
                    
                    # Display first few results
                    for i, car in enumerate(results['cars'][:5]):
                        print(f"\n🚗 {i+1}. {car['brand']} {car['model']}")
                        print(f"   💰 Price: {car['price']:,} MAD")
                        print(f"   📅 Year: {car['year']}")
                        print(f"   📍 Location: {car['city']}")
                        print(f"   🔗 URL: {car['url']}")
                        print(f"   ⛽ Fuel: {car['fuel_type']} | 🔧 Transmission: {car['transmission']}")
                    
                    return results['cars']
                    
                elif status['status'] == 'error':
                    print(f"❌ Scraping failed: {status['message']}")
                    return []
                
                time.sleep(2)  # Wait 2 seconds before checking again
                
        else:
            print(f"❌ Failed to start scraping: {response.text}")
            return []
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to scraping API. Make sure it's running on port 8001")
        return []

def quick_search_example():
    """
    Example of using the quick search endpoints
    """
    
    # Quick search for BMW
    try:
        response = requests.get(f"{API_BASE}/quick-search/BMW")
        if response.status_code == 200:
            print("✅ Quick search for BMW started")
            return True
    except:
        return False
    
    return False

def test_api_connection():
    """
    Test if the API is running
    """
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            print("✅ API is running successfully")
            return True
        else:
            print("❌ API returned error")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API is not running. Start it with: python used_cars_api.py")
        return False

# Frontend JavaScript example
frontend_example = """
// Example JavaScript code for your frontend

// Search for specific car
async function searchUsedCars(brand, model, maxPrice) {
    const response = await fetch('http://localhost:8001/search-cars', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            brand: brand,
            model: model,
            max_price: maxPrice,
            source: 'both'
        })
    });
    
    if (response.ok) {
        const result = await response.json();
        console.log('Scraping started:', result.message);
        
        // Monitor progress
        const checkStatus = setInterval(async () => {
            const statusResponse = await fetch('http://localhost:8001/scraping-status');
            const status = await statusResponse.json();
            
            console.log(`Progress: ${status.progress}% - ${status.message}`);
            updateProgressBar(status.progress, status.message);
            
            if (status.status === 'completed') {
                clearInterval(checkStatus);
                
                // Get results
                const resultsResponse = await fetch('http://localhost:8001/scraped-results');
                const results = await resultsResponse.json();
                
                displayResults(results.cars);
            } else if (status.status === 'error') {
                clearInterval(checkStatus);
                showError(status.message);
            }
        }, 2000);
    }
}

// Quick search
async function quickSearch(brand) {
    const response = await fetch(`http://localhost:8001/quick-search/${brand}`);
    if (response.ok) {
        console.log('Quick search started for', brand);
    }
}

// Display results in your UI
function displayResults(cars) {
    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = '';
    
    cars.forEach(car => {
        const carElement = document.createElement('div');
        carElement.className = 'car-result';
        carElement.innerHTML = `
            <h3>${car.brand} ${car.model}</h3>
            <p>Price: ${car.price.toLocaleString()} MAD</p>
            <p>Year: ${car.year}</p>
            <p>Location: ${car.city}</p>
            <a href="${car.url}" target="_blank">View on ${car.source}</a>
        `;
        resultsContainer.appendChild(carElement);
    });
}
"""

if __name__ == "__main__":
    print("🚗 Morocco Used Cars Scraper - Integration Example")
    print("=" * 55)
    
    # Test API connection
    if test_api_connection():
        # Example search
        cars = search_used_cars("BMW", "X5", 500000)
        
        if cars:
            print(f"\n📊 Successfully found {len(cars)} cars")
        else:
            print("❌ No cars found or scraping failed")
    
    # Print frontend example
    print("\n" + "="*55)
    print("📋 FRONTEND INTEGRATION EXAMPLE:")
    print("="*55)
    print(frontend_example)
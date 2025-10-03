@echo off
echo 🚗 Morocco Used Cars Scraper - Starting Services
echo ================================================

echo 📦 Installing Scrapy dependencies...
python setup_scrapers.py

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Setup failed
    pause
    exit /b 1
)

echo.
echo 🚀 Starting Used Cars API Server on port 8001...
echo    API will be available at: http://localhost:8001
echo    API Docs: http://localhost:8001/docs
echo.
echo 📋 Available endpoints:
echo    POST /search-cars - Search for specific cars
echo    GET /scraping-status - Check scraping progress  
echo    GET /scraped-results - Get latest results
echo    GET /quick-search/{brand} - Quick brand search
echo    GET /test-scrapers - Test if scrapers work
echo.
echo 💡 Example frontend calls:
echo    fetch('http://localhost:8001/search-cars', {
echo      method: 'POST', 
echo      headers: {'Content-Type': 'application/json'},
echo      body: JSON.stringify({brand: 'BMW', model: 'X5', max_price: 500000})
echo    })
echo.

python used_cars_api.py
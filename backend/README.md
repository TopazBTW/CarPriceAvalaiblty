# Car Price Prediction Backend

A FastAPI backend for predicting car prices in Morocco with web scraping integration.

## Features

- **ML Model**: Train and predict car prices using ensemble methods (RandomForest + GradientBoosting)
- **Web Scraping**: Fetch real market data from Avito.ma and Moteur.ma
- **Caching**: 15-minute TTL cache for scraping results
- **CORS Support**: Ready for frontend integration
- **Robust Error Handling**: Comprehensive logging and error management

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Start the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation:
Visit `http://localhost:8000/docs` for interactive API documentation.

## API Endpoints

### 1. Health Check
```
GET /health
```

### 2. Upload Training Data
```
POST /upload-csv
```
Upload a CSV file with car data to train the ML model.

**Required CSV columns:**
- Brand, Model, Year, KM_Driven, Fuel, Seller_Type, Transmission, Owner, Selling_Price

### 3. Predict Car Price
```
POST /predict
```

**Request body:**
```json
{
  "Brand": "Toyota",
  "Model": "Yaris",
  "Year": 2018,
  "KM_Driven": 80000,
  "Fuel": "Petrol",
  "Seller_Type": "Individual",
  "Transmission": "Manual",
  "Owner": "First Owner"
}
```

**Response:**
```json
{
  "predicted_price": 135000,
  "currency": "MAD",
  "market_avg_price": 140000,
  "listings": [
    {
      "title": "Toyota Yaris 2018, 85.000km",
      "price": 138000,
      "url": "https://www.avito.ma/fr/voitures/123456"
    }
  ],
  "model_confidence": 0.87,
  "scraping_source": "avito.ma"
}
```

## Scraping Sources

- **Avito.ma**: Primary source for car listings
- **Moteur.ma**: Fallback source if Avito fails

## Performance Features

- **Caching**: Results cached for 15 minutes
- **Limit**: Max 15 listings per search
- **Fuzzy Matching**: Handles model name variations
- **Price Filtering**: Removes unrealistic prices (10K-2M MAD)

## Error Handling

- Network timeouts (30 seconds)
- Missing model scenarios
- Invalid price ranges
- Comprehensive logging

## Development

### Test scraping functions:
```bash
python scrapers.py
```

### Model training tips:
- Ensure CSV has at least 100+ samples
- Remove outliers in price data
- Include diverse car brands and models

## File Structure

```
backend/
├── main.py          # FastAPI application
├── ml_model.py      # ML model class
├── scrapers.py      # Web scraping functions
├── requirements.txt # Dependencies
└── README.md       # This file
```
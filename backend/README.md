# Morocco Car Price Prediction API 🚗# Car Price Prediction Backend



Backend API for car price prediction using machine learning based on Morocco car market data.A FastAPI backend for predicting car prices in Morocco with web scraping integration.



## 📁 Project Structure## Features



```- **ML Model**: Train and predict car prices using ensemble methods (RandomForest + GradientBoosting)

backend/- **Web Scraping**: Fetch real market data from Avito.ma and Moteur.ma

├── config/                 # Configuration files- **Caching**: 15-minute TTL cache for scraping results

│   ├── config.py          # App configuration- **CORS Support**: Ready for frontend integration

│   ├── requirements.txt   # Python dependencies- **Robust Error Handling**: Comprehensive logging and error management

│   └── __init__.py

│## Installation

├── data/                   # Data storage

│   ├── csv/               # CSV datasets1. Create a virtual environment:

│   │   └── morocco_used_cars.csv (10,000 cars)```bash

│   └── json/              # JSON datapython -m venv venv

│source venv/bin/activate  # On Windows: venv\Scripts\activate

├── models/                 # ML models```

│   ├── ml_model.py        # Model training & prediction

│   ├── car_price_model.joblib  # Trained model2. Install dependencies:

│   └── __init__.py```bash

│pip install -r requirements.txt

├── scrapers/               # Data collection```

│   ├── kifal_scraper.py   # Car scraping utilities

│   └── __init__.py## Usage

│

├── utils/                  # Utility functions### Start the server:

│   ├── process_kifal_data.py```bash

│   └── __init__.pypython main.py

│```

├── deployment/             # Docker & deployment

│   ├── DockerfileThe API will be available at `http://localhost:8000`

│   ├── docker-compose.yml

│   └── start.bat### API Documentation:

│Visit `http://localhost:8000/docs` for interactive API documentation.

├── tests/                  # Unit tests

│   └── __init__.py## API Endpoints

│

├── used_cars_api.py        # Main FastAPI application### 1. Health Check

├── test_api.py             # API testing```

├── generate_market_data.py # Dataset generatorGET /health

└── README.md```

```

### 2. Upload Training Data

## 🚀 Quick Start```

POST /upload-csv

### Installation```

Upload a CSV file with car data to train the ML model.

```bash

# Install dependencies**Required CSV columns:**

pip install -r config/requirements.txt- Brand, Model, Year, KM_Driven, Fuel, Seller_Type, Transmission, Owner, Selling_Price

```

### 3. Predict Car Price

### Run API Server```

POST /predict

```bash```

# Start FastAPI server

python used_cars_api.py**Request body:**

```json

# Or using uvicorn{

uvicorn used_cars_api:app --reload  "Brand": "Toyota",

```  "Model": "Yaris",

  "Year": 2018,

API will be available at: `http://localhost:8000`  "KM_Driven": 80000,

  "Fuel": "Petrol",

## 📊 Dataset  "Seller_Type": "Individual",

  "Transmission": "Manual",

- **Size**: 10,000 cars  "Owner": "First Owner"

- **Source**: Morocco market data (2025)}

- **Brands**: Dacia, Renault, Peugeot, Toyota, Hyundai, VW, etc.```

- **Features**: Brand, Model, Year, KM, Fuel, Transmission, Condition, Location

**Response:**

## 🔥 API Endpoints```json

{

### `GET /`  "predicted_price": 135000,

Health check endpoint  "currency": "MAD",

  "market_avg_price": 140000,

### `GET /cars`  "listings": [

Get all cars with optional filtering    {

- Query params: brand, year_min, year_max, price_min, price_max      "title": "Toyota Yaris 2018, 85.000km",

      "price": 138000,

### `GET /cars/{car_id}`      "url": "https://www.avito.ma/fr/voitures/123456"

Get specific car by ID    }

  ],

### `POST /predict`  "model_confidence": 0.87,

Predict car price  "scraping_source": "avito.ma"

```json}

{```

  "brand": "Dacia",

  "model": "Logan",## Scraping Sources

  "year": 2020,

  "km_driven": 80000,- **Avito.ma**: Primary source for car listings

  "fuel_type": "Gasoline",- **Moteur.ma**: Fallback source if Avito fails

  "transmission": "Manual",

  "condition": "Good",## Performance Features

  "location": "Casablanca"

}- **Caching**: Results cached for 15 minutes

```- **Limit**: Max 15 listings per search

- **Fuzzy Matching**: Handles model name variations

### `GET /stats`- **Price Filtering**: Removes unrealistic prices (10K-2M MAD)

Get dataset statistics

## Error Handling

## 🛠 Technologies

- Network timeouts (30 seconds)

- **FastAPI**: Modern web framework- Missing model scenarios

- **Pandas**: Data manipulation- Invalid price ranges

- **Scikit-learn**: Machine learning- Comprehensive logging

- **Uvicorn**: ASGI server

- **Pydantic**: Data validation## Development



## 📝 License### Test scraping functions:

```bash

MIT Licensepython scrapers.py

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
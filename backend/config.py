"""
Configuration settings for the Car Price Prediction API
"""

import os
from typing import Dict, List

# Server Configuration
SERVER_HOST = os.getenv("HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("PORT", 8000))
DEBUG_MODE = os.getenv("DEBUG", "True").lower() == "true"
RELOAD = os.getenv("RELOAD", "True").lower() == "true"

# Model Configuration
MODEL_PATH = os.getenv("MODEL_PATH", "car_price_model.joblib")
MIN_TRAINING_SAMPLES = int(os.getenv("MIN_TRAINING_SAMPLES", 50))
MAX_PRICE = int(os.getenv("MAX_PRICE", 2000000))  # Maximum reasonable car price in MAD
MIN_PRICE = int(os.getenv("MIN_PRICE", 10000))    # Minimum reasonable car price in MAD

# Scraping Configuration
SCRAPING_TIMEOUT = int(os.getenv("SCRAPING_TIMEOUT", 30))  # seconds
MAX_LISTINGS_PER_SOURCE = int(os.getenv("MAX_LISTINGS", 15))
CACHE_TTL = int(os.getenv("CACHE_TTL", 900))  # 15 minutes in seconds
FUZZY_MATCH_THRESHOLD = float(os.getenv("FUZZY_THRESHOLD", 0.6))

# Request Configuration
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 10 * 1024 * 1024))  # 10MB

# CORS Configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
ALLOWED_HEADERS = ["*"]

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Website URLs for scraping
SCRAPING_SOURCES = {
    "avito": {
        "base_url": "https://www.avito.ma",
        "search_path": "/fr/maroc/voitures-à_vendre",
        "enabled": True
    },
    "moteur": {
        "base_url": "https://www.moteur.ma", 
        "search_path": "/fr/voiture/recherche.html",
        "enabled": True
    }
}

# User agents for scraping (rotate to avoid detection)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
]

# Common car brands and models in Morocco
MOROCCO_CAR_BRANDS = {
    "Toyota": ["Yaris", "Corolla", "Camry", "RAV4", "Prius", "Hilux", "Land Cruiser"],
    "Honda": ["Civic", "Accord", "CR-V", "City", "Jazz", "Pilot"],
    "Nissan": ["Micra", "Sentra", "Qashqai", "X-Trail", "Patrol", "Navara"],
    "Hyundai": ["Accent", "Elantra", "Tucson", "Santa Fe", "i10", "i20"],
    "Kia": ["Rio", "Cerato", "Sportage", "Sorento", "Picanto"],
    "Ford": ["Focus", "Fiesta", "Mondeo", "Kuga", "EcoSport"],
    "Volkswagen": ["Golf", "Polo", "Passat", "Tiguan", "Touareg"],
    "Peugeot": ["208", "308", "508", "2008", "3008", "5008"],
    "Renault": ["Clio", "Megane", "Captur", "Kadjar", "Koleos"],
    "Dacia": ["Logan", "Sandero", "Duster", "Lodgy"],
    "Mercedes": ["A-Class", "C-Class", "E-Class", "GLA", "GLC"],
    "BMW": ["Serie 1", "Serie 3", "Serie 5", "X1", "X3", "X5"],
    "Audi": ["A3", "A4", "A6", "Q3", "Q5", "Q7"],
}

# Feature importance weights for price prediction
FEATURE_WEIGHTS = {
    "Brand": 0.25,
    "Model": 0.20,
    "Year": 0.25,
    "KM_Driven": 0.15,
    "Fuel": 0.05,
    "Transmission": 0.05,
    "Owner": 0.05
}

# Price adjustment factors
BRAND_PREMIUM = {
    "Mercedes": 1.4,
    "BMW": 1.3,
    "Audi": 1.25,
    "Toyota": 1.1,
    "Honda": 1.05,
    "Nissan": 1.0,
    "Hyundai": 0.9,
    "Kia": 0.85,
    "Ford": 0.8,
    "Peugeot": 0.75,
    "Renault": 0.7,
    "Dacia": 0.6
}

FUEL_PREMIUM = {
    "Electric": 1.3,
    "Diesel": 1.1,
    "Petrol": 1.0,
    "CNG": 0.9
}

TRANSMISSION_PREMIUM = {
    "Automatic": 1.15,
    "Manual": 1.0
}

OWNER_DISCOUNT = {
    "First Owner": 1.0,
    "Second Owner": 0.85,
    "Third Owner": 0.7,
    "Fourth & Above Owner": 0.6
}

# ML Model parameters
ML_CONFIG = {
    "test_size": 0.2,
    "random_state": 42,
    "n_estimators": 100,
    "max_depth": 15,
    "min_samples_split": 5,
    "min_samples_leaf": 2,
    "validation_split": 0.1
}
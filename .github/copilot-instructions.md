# GitHub Copilot Instructions for CarPredict Project

## Project Overview
CarPredict is a car price prediction platform for the Morocco market consisting of a FastAPI backend with ML models and web scrapers, and a Next.js 14 frontend with modern React components. The platform predicts used car prices and scrapes real-time market data from Morocco automotive websites.

## Architecture

### Backend (`/backend/`)
- **Framework**: FastAPI with uvicorn server
- **Main API**: `used_cars_api.py` (primary application entry point)
- **ML Engine**: `models/ml_model.py` (ensemble RandomForest + GradientBoosting)  
- **Data Collection**: Multiple scrapers in `scrapers/` for Morocco car sites
- **Configuration**: `config/config.py` with environment variables
- **Server Start**: `start_server.py` or `python used_cars_api.py`

### Frontend (`/Front/`)
- **Framework**: Next.js 14 with TypeScript
- **UI Library**: Radix UI components with Tailwind CSS
- **Architecture**: App Router pattern with component-based structure
- **Entry Point**: `app/page.tsx` (main homepage)
- **Key Components**: Car selection forms, price display, search interfaces

## Key Development Patterns

### Backend API Patterns
```python
# Standard FastAPI endpoint structure
@app.post("/endpoint-name")  
async def endpoint_function(request: RequestModel, background_tasks: BackgroundTasks):
    # CORS is already configured globally
    # Use background tasks for long-running operations like scraping
    return {"status": "success", "data": result}

# ML Model usage pattern
from models.ml_model import MLModel
model = MLModel()
prediction = model.predict(car_data)  # Returns dict with price and confidence
```

### Frontend API Integration
```typescript
// Standard fetch pattern - backend runs on localhost:8000
const response = await fetch('http://localhost:8000/endpoint')
const data = await response.json()

// Component state management
const [brands, setBrands] = useState<any[]>([])
const [models, setModels] = useState<any[]>([])
```

### Component Patterns
- **Radix UI Select**: Always use non-empty values (`"no-brand"` instead of `""`)
- **Form Handling**: React Hook Form with Zod validation
- **Layout**: Consistent container/padding using Tailwind classes
- **Typography**: GeistSans font family configured globally

## Data Flow Architecture

### Car Price Prediction Flow
1. **Frontend**: User selects car details (brand, model, year, mileage, fuel type)
2. **API Call**: POST to `/predict` with car specifications
3. **ML Processing**: `MLModel.predict()` processes data through ensemble model
4. **Response**: Returns predicted price, confidence score, and market data

### Real-Time Scraping Flow  
1. **Trigger**: POST to `/search-cars` with search criteria
2. **Background Task**: Asynchronous scraping from Avito.ma and other sources
3. **Status Polling**: GET `/scraping-status` for progress updates
4. **Results**: GET `/scraped-results` for final car listings

### Brand/Model Data Flow
- **Brands**: GET `/brands` returns available car brands
- **Models**: GET `/brands/{brand}/models` returns models for specific brand
- **Static Data**: Stored in `backend/data/json/` directory

## File Structure Significance

### Backend Critical Files
- `used_cars_api.py`: Main FastAPI application with all endpoints
- `models/ml_model.py`: Core ML prediction engine
- `config/config.py`: Environment configuration and constants
- `start_server.py`: Server startup script
- `scrapers/kifal_scraper.py`: Primary Morocco car data scraper

### Frontend Critical Files  
- `app/page.tsx`: Homepage with main car selection interface
- `components/new-cars-hero.tsx`: Primary car search component
- `components/hero-section.tsx`: Used car valuation form
- `next.config.mjs`: Next.js configuration with TypeScript/ESLint overrides

## Development Guidelines

### Backend Development
1. **Environment Setup**: Use Python virtual environment with `requirements.txt`
2. **Server Launch**: `python start_server.py` or `uvicorn used_cars_api:app --reload`
3. **ML Model**: Pre-trained model exists at `models/car_price_model.joblib`
4. **Data Sources**: JSON files in `data/json/` for brands/models/pricing

### Frontend Development
1. **Environment**: Node.js with pnpm package manager
2. **Development**: `pnpm dev` for local development server
3. **API Integration**: All backend calls use `http://localhost:8000` base URL
4. **Styling**: Tailwind CSS with Radix UI component library

### Code Style Preferences
- **Python**: FastAPI async patterns, Pydantic models for validation
- **TypeScript**: Strict typing, functional components with hooks
- **Error Handling**: Comprehensive try/catch with user-friendly error messages
- **Logging**: Structured logging for debugging and monitoring

## Common Development Tasks

### Adding New API Endpoints
```python
# In used_cars_api.py
@app.post("/new-endpoint")
async def new_endpoint(request: RequestModel):
    # Add CORS headers automatically included
    # Implement business logic
    return {"success": True, "data": result}
```

### Adding New Frontend Components  
```typescript
// In components/
export function NewComponent() {
  // Use Radix UI components
  // Apply Tailwind styling
  // Handle API integration with fetch
  return <div>Component JSX</div>
}
```

### ML Model Operations
```python
# Training new model
model = MLModel()
model.train(dataframe)  # Requires specific column structure
model.save_model()

# Making predictions  
prediction = model.predict({
    "Brand": "Toyota", "Model": "Corolla", 
    "Year": 2020, "KM_Driven": 50000,
    "Fuel": "Petrol", "Transmission": "Manual"
})
```

## Troubleshooting Common Issues

### Backend Issues
- **Import Errors**: Ensure working directory is `/backend/` when running Python scripts
- **Port Conflicts**: Default port 8000, change in `config/config.py` if needed  
- **Model Loading**: Verify `models/car_price_model.joblib` exists and is accessible
- **CORS Issues**: CORS middleware configured for all origins (`["*"]`)

### Frontend Issues
- **API Connection**: Verify backend is running on localhost:8000
- **Select Components**: Use non-empty string values for Radix UI Select items
- **Build Errors**: TypeScript/ESLint errors ignored in build (see `next.config.mjs`)
- **Styling Issues**: Verify Tailwind classes and Radix UI component structure

### Integration Issues
- **Data Format Mismatch**: Ensure API responses match frontend TypeScript interfaces
- **Authentication**: No authentication currently implemented
- **Environment Variables**: Check both frontend and backend environment configurations

## Testing Strategies

### Backend Testing
```bash
# API testing script available
python test_api.py

# Direct endpoint testing
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{...}'
```

### Frontend Testing
```bash
# Component development
pnpm dev  # Run development server
# Test API integration in browser network tab
```

## Deployment Considerations

### Backend Deployment
- **Docker**: `deployment/Dockerfile` available for containerization
- **Dependencies**: `config/requirements.txt` for production dependencies  
- **Environment**: Set production environment variables in `config/config.py`

### Frontend Deployment
- **Build**: `pnpm build` for production build
- **Static Export**: Images unoptimized for static hosting compatibility
- **API URL**: Update backend URL for production deployment

## Data Specifications

### ML Model Input Format
Required fields for price prediction:
```json
{
  "Brand": "string",
  "Model": "string", 
  "Year": "integer",
  "KM_Driven": "integer",
  "Fuel": "string (Petrol/Diesel/Electric)",
  "Transmission": "string (Manual/Automatic)",
  "Seller_Type": "string",
  "Owner": "string"
}
```

### Scraping Data Format
Car listing structure:
```json
{
  "brand": "string",
  "model": "string",
  "year": "integer",
  "price": "integer (MAD)",
  "mileage": "integer", 
  "fuel_type": "string",
  "transmission": "string",
  "city": "string",
  "url": "string",
  "source": "string"
}
```

## Morocco Market Context
- **Currency**: Moroccan Dirham (MAD)
- **Price Range**: 10,000 - 2,000,000 MAD for reasonable car prices
- **Popular Brands**: Dacia, Renault, Peugeot, Toyota, Hyundai, Volkswagen
- **Data Sources**: Kifal.ma, Avito.ma, Moteur.ma for market data
- **Cities**: Casablanca, Rabat, Marrakech, Fez, Tangier as major markets

---

*This file should be updated as the project evolves. Key areas to monitor: API endpoint changes, new ML model features, frontend component patterns, and integration requirements.*
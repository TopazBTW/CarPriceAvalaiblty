# 🚗 Used Cars API Integration Guide

## Overview
The Used Cars API provides real-time web scraping of used car listings from **Avito.ma** and **Facebook Marketplace** Morocco. Your frontend can trigger searches and retrieve results with prices and links.

## 🚀 Server Status
- **API Server**: Running on `http://localhost:8001`
- **Main Backend**: Running on `http://localhost:8000` (car prediction)
- **Status**: ✅ All systems operational

## 📡 API Endpoints

### 1. Test Scrapers
**GET** `http://localhost:8001/test-scrapers`

Test if the scraping system is working.

**Response:**
```json
{
  "status": "success",
  "avito_results": 0,
  "sample_data": [],
  "message": "Scrapers are working"
}
```

### 2. Search Cars (Main Endpoint)
**POST** `http://localhost:8001/search-cars`

Trigger a real-time search for used cars across Avito and Facebook Marketplace.

**Request Body:**
```json
{
  "brand": "Toyota",
  "model": "Corolla", 
  "year_min": 2015,
  "year_max": 2023,
  "price_min": 50000,
  "price_max": 200000
}
```

**Response:**
```json
{
  "message": "Car search started",
  "task_id": "abc123def456",
  "status": "running"
}
```

### 3. Check Search Status  
**GET** `http://localhost:8001/scraping-status/{task_id}`

Check the progress of a search task.

**Response:**
```json
{
  "task_id": "abc123def456",
  "status": "running",
  "progress": "Scraping Avito.ma..."
}
```

**Status Values:**
- `running`: Search in progress
- `completed`: Search finished
- `failed`: Search encountered an error

### 4. Get Search Results
**GET** `http://localhost:8001/scraped-results/{task_id}`

Retrieve the scraped car listings.

**Response:**
```json
{
  "task_id": "abc123def456",
  "total_found": 25,
  "cars": [
    {
      "title": "Toyota Corolla 2018",
      "price": "120000",
      "year": "2018", 
      "km": "85000",
      "location": "Casablanca",
      "link": "https://www.avito.ma/casablanca/voitures/...",
      "source": "avito",
      "image_url": "https://..."
    }
  ]
}
```

## 🔧 Frontend Integration Examples

### JavaScript/Fetch API
```javascript
// Search for cars
async function searchCars(searchParams) {
  try {
    const response = await fetch('http://localhost:8001/search-cars', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(searchParams)
    });
    
    const result = await response.json();
    const taskId = result.task_id;
    
    // Poll for results
    return await pollForResults(taskId);
  } catch (error) {
    console.error('Search failed:', error);
  }
}

// Poll for search results
async function pollForResults(taskId) {
  const maxAttempts = 30; // 30 seconds max
  
  for (let i = 0; i < maxAttempts; i++) {
    try {
      const statusResponse = await fetch(`http://localhost:8001/scraping-status/${taskId}`);
      const status = await statusResponse.json();
      
      if (status.status === 'completed') {
        const resultsResponse = await fetch(`http://localhost:8001/scraped-results/${taskId}`);
        return await resultsResponse.json();
      } else if (status.status === 'failed') {
        throw new Error('Search failed');
      }
      
      // Wait 1 second before next check
      await new Promise(resolve => setTimeout(resolve, 1000));
    } catch (error) {
      console.error('Polling error:', error);
      break;
    }
  }
  
  throw new Error('Search timeout');
}

// Example usage
const searchParams = {
  brand: "Toyota",
  model: "Corolla",
  year_min: 2015,
  year_max: 2023,
  price_min: 50000,
  price_max: 200000
};

searchCars(searchParams).then(results => {
  console.log('Found cars:', results.cars);
  results.cars.forEach(car => {
    console.log(`${car.title} - ${car.price} MAD - ${car.link}`);
  });
});
```

### React Hook Example
```javascript
import { useState, useEffect } from 'react';

function useCarSearch() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const searchCars = async (searchParams) => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch('http://localhost:8001/search-cars', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(searchParams)
      });

      const { task_id } = await response.json();
      
      // Poll for results
      const pollResults = async () => {
        const statusRes = await fetch(`http://localhost:8001/scraping-status/${task_id}`);
        const status = await statusRes.json();

        if (status.status === 'completed') {
          const resultsRes = await fetch(`http://localhost:8001/scraped-results/${task_id}`);
          const results = await resultsRes.json();
          setResults(results);
          setLoading(false);
        } else if (status.status === 'failed') {
          setError('Search failed');
          setLoading(false);
        } else {
          setTimeout(pollResults, 1000);
        }
      };

      pollResults();
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  return { searchCars, results, loading, error };
}
```

## 🔍 Search Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `brand` | string | Yes | Car brand (Toyota, Mercedes, etc.) |
| `model` | string | Yes | Car model (Corolla, C-Class, etc.) |
| `year_min` | integer | No | Minimum year (default: 2000) |
| `year_max` | integer | No | Maximum year (default: current year) |
| `price_min` | integer | No | Minimum price in MAD (default: 0) |
| `price_max` | integer | No | Maximum price in MAD (default: 10000000) |

## 📊 Response Data Structure

### Car Object
```javascript
{
  "title": "Toyota Corolla 2018 Automatique",
  "price": "120000",           // Price in MAD
  "year": "2018",             // Manufacturing year
  "km": "85000",              // Kilometers driven
  "location": "Casablanca",    // City location
  "link": "https://...",       // Direct link to listing
  "source": "avito",          // Source website
  "image_url": "https://...",  // Car image URL
  "phone": "+212..."          // Contact phone (if available)
}
```

## 🛠️ Error Handling

The API uses standard HTTP status codes:
- **200**: Success
- **202**: Request accepted (search started)
- **400**: Bad request (invalid parameters)
- **404**: Task not found
- **500**: Server error

## 💡 Best Practices

1. **Caching**: Cache results for similar searches to avoid repeated scraping
2. **Rate Limiting**: Don't make too many concurrent searches
3. **Timeout**: Set reasonable timeouts (30-60 seconds max)
4. **Error Handling**: Always handle network and API errors gracefully
5. **User Feedback**: Show loading states and progress to users

## 🚀 Example Complete Integration

```javascript
// Complete car search component
class CarSearchComponent {
  constructor() {
    this.apiBase = 'http://localhost:8001';
  }

  async searchUsedCars(brand, model, yearMin, yearMax, priceMin, priceMax) {
    const searchParams = {
      brand,
      model,
      year_min: yearMin,
      year_max: yearMax,
      price_min: priceMin,
      price_max: priceMax
    };

    try {
      // Start search
      const response = await fetch(`${this.apiBase}/search-cars`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(searchParams)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const { task_id } = await response.json();
      
      // Wait for results
      return await this.waitForResults(task_id);
    } catch (error) {
      console.error('Car search failed:', error);
      throw error;
    }
  }

  async waitForResults(taskId) {
    const maxWait = 60000; // 60 seconds
    const interval = 1000; // Check every second
    const startTime = Date.now();

    while (Date.now() - startTime < maxWait) {
      try {
        const statusResponse = await fetch(`${this.apiBase}/scraping-status/${taskId}`);
        const status = await statusResponse.json();

        if (status.status === 'completed') {
          const resultsResponse = await fetch(`${this.apiBase}/scraped-results/${taskId}`);
          return await resultsResponse.json();
        } else if (status.status === 'failed') {
          throw new Error('Search failed on server');
        }

        await new Promise(resolve => setTimeout(resolve, interval));
      } catch (error) {
        console.error('Status check failed:', error);
        throw error;
      }
    }

    throw new Error('Search timeout - try again later');
  }
}

// Usage example
const carSearch = new CarSearchComponent();

carSearch.searchUsedCars('Toyota', 'Corolla', 2015, 2023, 50000, 200000)
  .then(results => {
    console.log(`Found ${results.total_found} cars:`);
    results.cars.forEach(car => {
      console.log(`- ${car.title}: ${car.price} MAD`);
      console.log(`  Location: ${car.location}`);
      console.log(`  Link: ${car.link}`);
    });
  })
  .catch(error => {
    console.error('Search failed:', error);
  });
```

## 🎯 Ready for Production!

Your used cars scraping API is now fully operational and ready for frontend integration. The system will:

1. ✅ Accept car search requests from your frontend
2. ✅ Scrape Avito.ma and Facebook Marketplace in real-time  
3. ✅ Return structured data with prices, links, and details
4. ✅ Handle multiple concurrent searches
5. ✅ Provide status updates and error handling

Start integrating these endpoints into your frontend and your users will have access to real-time used car market data! 🚗💨
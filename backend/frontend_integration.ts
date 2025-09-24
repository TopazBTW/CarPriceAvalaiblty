// Frontend integration for Morocco Car Price Prediction
// This file should be added to your Next.js frontend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface CarPredictionRequest {
  Brand: string;
  Model: string;
  Year: number;
  KM_Driven: number;
  Fuel: string;
  Seller_Type: string;
  Transmission: string;
  Owner: string;
}

export interface CarListing {
  title: string;
  price: number;
  url: string;
}

export interface PredictionResponse {
  predicted_price: number;
  currency: string;
  market_avg_price?: number;
  listings: CarListing[];
  model_confidence: number;
  scraping_source: string;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  model_loaded: boolean;
  scraping_enabled: boolean;
}

class CarPriceAPI {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async checkHealth(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }
    return response.json();
  }

  async predictPrice(carData: CarPredictionRequest): Promise<PredictionResponse> {
    const response = await fetch(`${this.baseUrl}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(carData),
    });

    if (!response.ok) {
      const errorData = await response.text();
      throw new Error(`Prediction failed: ${errorData}`);
    }

    return response.json();
  }

  async uploadTrainingData(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/upload-csv`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.text();
      throw new Error(`Upload failed: ${errorData}`);
    }

    return response.json();
  }
}

export const carPriceAPI = new CarPriceAPI();

// React Hook for using the API
import { useState, useEffect } from 'react';

export function useCarPriceAPI() {
  const [isHealthy, setIsHealthy] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkApiHealth = async () => {
      try {
        await carPriceAPI.checkHealth();
        setIsHealthy(true);
      } catch (error) {
        console.error('API health check failed:', error);
        setIsHealthy(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkApiHealth();
  }, []);

  return { isHealthy, isLoading, api: carPriceAPI };
}

// Example React component for car price prediction
export function CarPricePredictionForm() {
  const { isHealthy, isLoading, api } = useCarPriceAPI();
  const [formData, setFormData] = useState<CarPredictionRequest>({
    Brand: 'Toyota',
    Model: 'Yaris',
    Year: new Date().getFullYear() - 2,
    KM_Driven: 50000,
    Fuel: 'Petrol',
    Seller_Type: 'Individual',
    Transmission: 'Manual',
    Owner: 'First Owner',
  });
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [predicting, setPredicting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setPredicting(true);
    setError(null);

    try {
      const result = await api.predictPrice(formData);
      setPrediction(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Prediction failed');
    } finally {
      setPredicting(false);
    }
  };

  if (isLoading) {
    return <div className="p-4">Connecting to price prediction service...</div>;
  }

  if (!isHealthy) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded">
        <p className="text-red-700">Price prediction service is unavailable</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6">Car Price Prediction</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Brand</label>
            <select
              value={formData.Brand}
              onChange={(e) => setFormData({...formData, Brand: e.target.value})}
              className="w-full p-2 border rounded"
              required
            >
              {['Toyota', 'Honda', 'Nissan', 'Hyundai', 'Kia', 'Ford', 'Volkswagen', 'Peugeot', 'Renault', 'Dacia'].map(brand => (
                <option key={brand} value={brand}>{brand}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Model</label>
            <input
              type="text"
              value={formData.Model}
              onChange={(e) => setFormData({...formData, Model: e.target.value})}
              className="w-full p-2 border rounded"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Year</label>
            <input
              type="number"
              value={formData.Year}
              onChange={(e) => setFormData({...formData, Year: parseInt(e.target.value)})}
              min="2000"
              max={new Date().getFullYear()}
              className="w-full p-2 border rounded"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Kilometers Driven</label>
            <input
              type="number"
              value={formData.KM_Driven}
              onChange={(e) => setFormData({...formData, KM_Driven: parseInt(e.target.value)})}
              min="0"
              className="w-full p-2 border rounded"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Fuel Type</label>
            <select
              value={formData.Fuel}
              onChange={(e) => setFormData({...formData, Fuel: e.target.value})}
              className="w-full p-2 border rounded"
              required
            >
              {['Petrol', 'Diesel', 'CNG', 'Electric'].map(fuel => (
                <option key={fuel} value={fuel}>{fuel}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Seller Type</label>
            <select
              value={formData.Seller_Type}
              onChange={(e) => setFormData({...formData, Seller_Type: e.target.value})}
              className="w-full p-2 border rounded"
              required
            >
              {['Individual', 'Dealer'].map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Transmission</label>
            <select
              value={formData.Transmission}
              onChange={(e) => setFormData({...formData, Transmission: e.target.value})}
              className="w-full p-2 border rounded"
              required
            >
              {['Manual', 'Automatic'].map(trans => (
                <option key={trans} value={trans}>{trans}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Owner</label>
            <select
              value={formData.Owner}
              onChange={(e) => setFormData({...formData, Owner: e.target.value})}
              className="w-full p-2 border rounded"
              required
            >
              {['First Owner', 'Second Owner', 'Third Owner', 'Fourth & Above Owner'].map(owner => (
                <option key={owner} value={owner}>{owner}</option>
              ))}
            </select>
          </div>
        </div>

        <button
          type="submit"
          disabled={predicting}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {predicting ? 'Predicting...' : 'Get Price Prediction'}
        </button>
      </form>

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {prediction && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded">
          <h3 className="text-lg font-semibold mb-3">Price Prediction Results</h3>
          
          <div className="space-y-2">
            <p><strong>Predicted Price:</strong> {prediction.predicted_price.toLocaleString()} {prediction.currency}</p>
            {prediction.market_avg_price && (
              <p><strong>Market Average:</strong> {prediction.market_avg_price.toLocaleString()} {prediction.currency}</p>
            )}
            <p><strong>Confidence:</strong> {(prediction.model_confidence * 100).toFixed(1)}%</p>
            <p><strong>Data Source:</strong> {prediction.scraping_source}</p>
          </div>

          {prediction.listings.length > 0 && (
            <div className="mt-4">
              <h4 className="font-medium mb-2">Similar Listings:</h4>
              <ul className="space-y-1">
                {prediction.listings.map((listing, index) => (
                  <li key={index}>
                    <a
                      href={listing.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      {listing.title} - {listing.price.toLocaleString()} MAD
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
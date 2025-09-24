"use client"

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { AlertCircle, TrendingUp, ExternalLink, Car, DollarSign } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'

interface CarPredictionRequest {
  Brand: string;
  Model: string;
  Year: number;
  KM_Driven: number;
  Fuel: string;
  Seller_Type: string;
  Transmission: string;
  Owner: string;
}

interface CarListing {
  title: string;
  price: number;
  url: string;
}

interface PredictionResponse {
  predicted_price: number;
  currency: string;
  market_avg_price?: number;
  listings: CarListing[];
  model_confidence: number;
  scraping_source: string;
}

const API_BASE_URL = 'http://localhost:8001';

const moroccanBrands = [
  'Toyota', 'Honda', 'Nissan', 'Hyundai', 'Kia', 'Ford', 
  'Volkswagen', 'Peugeot', 'Renault', 'Dacia', 'Mercedes', 
  'BMW', 'Audi', 'Fiat', 'Opel', 'Skoda', 'SEAT'
];

const fuelTypes = ['Petrol', 'Diesel', 'Electric', 'Hybrid', 'CNG'];
const sellerTypes = ['Individual', 'Dealer'];
const transmissionTypes = ['Manual', 'Automatic'];
const ownerTypes = ['First Owner', 'Second Owner', 'Third Owner', 'Fourth & Above Owner'];

export function CarPricePrediction() {
  const [formData, setFormData] = useState<CarPredictionRequest>({
    Brand: '',
    Model: '',
    Year: new Date().getFullYear() - 2,
    KM_Driven: 50000,
    Fuel: '',
    Seller_Type: '',
    Transmission: '',
    Owner: ''
  });

  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      // Validate form
      const requiredFields = ['Brand', 'Model', 'Fuel', 'Seller_Type', 'Transmission', 'Owner'];
      for (const field of requiredFields) {
        if (!formData[field as keyof CarPredictionRequest]) {
          throw new Error(`Veuillez remplir le champ ${field}`);
        }
      }

      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(`Erreur de prédiction: ${errorData}`);
      }

      const result: PredictionResponse = await response.json();
      setPrediction(result);

    } catch (err) {
      console.error('Prediction error:', err);
      setError(err instanceof Error ? err.message : 'Erreur lors de la prédiction du prix');
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('fr-MA', {
      style: 'decimal',
      minimumFractionDigits: 0
    }).format(price);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Évaluation de Prix de Voiture
          </h1>
          <p className="text-gray-600">
            Obtenez une estimation précise du prix de votre voiture avec des données du marché marocain
          </p>
        </div>

        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Car className="h-5 w-5" />
              Informations du Véhicule
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium mb-2">Marque</label>
                  <Select value={formData.Brand} onValueChange={(value) => setFormData({...formData, Brand: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Sélectionner une marque" />
                    </SelectTrigger>
                    <SelectContent>
                      {moroccanBrands.map(brand => (
                        <SelectItem key={brand} value={brand}>{brand}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Modèle</label>
                  <Input
                    type="text"
                    value={formData.Model}
                    onChange={(e) => setFormData({...formData, Model: e.target.value})}
                    placeholder="Ex: Yaris, Civic, Clio..."
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Année</label>
                  <Input
                    type="number"
                    value={formData.Year}
                    onChange={(e) => setFormData({...formData, Year: parseInt(e.target.value)})}
                    min="1990"
                    max={new Date().getFullYear()}
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Kilométrage</label>
                  <Input
                    type="number"
                    value={formData.KM_Driven}
                    onChange={(e) => setFormData({...formData, KM_Driven: parseInt(e.target.value)})}
                    min="0"
                    placeholder="80000"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Carburant</label>
                  <Select value={formData.Fuel} onValueChange={(value) => setFormData({...formData, Fuel: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Type de carburant" />
                    </SelectTrigger>
                    <SelectContent>
                      {fuelTypes.map(fuel => (
                        <SelectItem key={fuel} value={fuel}>{fuel}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Type de vendeur</label>
                  <Select value={formData.Seller_Type} onValueChange={(value) => setFormData({...formData, Seller_Type: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Type de vendeur" />
                    </SelectTrigger>
                    <SelectContent>
                      {sellerTypes.map(type => (
                        <SelectItem key={type} value={type}>{type === 'Individual' ? 'Particulier' : 'Concessionnaire'}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Transmission</label>
                  <Select value={formData.Transmission} onValueChange={(value) => setFormData({...formData, Transmission: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Type de transmission" />
                    </SelectTrigger>
                    <SelectContent>
                      {transmissionTypes.map(trans => (
                        <SelectItem key={trans} value={trans}>{trans === 'Manual' ? 'Manuelle' : 'Automatique'}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Propriétaire</label>
                  <Select value={formData.Owner} onValueChange={(value) => setFormData({...formData, Owner: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Numéro du propriétaire" />
                    </SelectTrigger>
                    <SelectContent>
                      {ownerTypes.map(owner => (
                        <SelectItem key={owner} value={owner}>{owner.replace('First', 'Premier').replace('Second', 'Deuxième').replace('Third', 'Troisième').replace('Fourth & Above', 'Quatrième et plus')}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <Button 
                type="submit" 
                className="w-full" 
                disabled={loading}
                size="lg"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Recherche en cours...
                  </>
                ) : (
                  <>
                    <DollarSign className="h-4 w-4 mr-2" />
                    Obtenir l'Évaluation
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {error && (
          <Alert className="mb-6 border-red-200 bg-red-50">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="text-red-700">
              {error}
            </AlertDescription>
          </Alert>
        )}

        {prediction && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Résultats de l'Évaluation
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {formatPrice(prediction.predicted_price)} MAD
                    </div>
                    <div className="text-sm text-blue-500 mt-1">Prix Estimé (IA)</div>
                    <Badge variant="secondary" className="mt-2">
                      Confiance: {(prediction.model_confidence * 100).toFixed(1)}%
                    </Badge>
                  </div>

                  {prediction.market_avg_price && (
                    <div className="text-center p-4 bg-green-50 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">
                        {formatPrice(prediction.market_avg_price)} MAD
                      </div>
                      <div className="text-sm text-green-500 mt-1">Moyenne du Marché</div>
                      <Badge variant="outline" className="mt-2">
                        Source: {prediction.scraping_source}
                      </Badge>
                    </div>
                  )}

                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-gray-600">
                      {prediction.listings.length}
                    </div>
                    <div className="text-sm text-gray-500 mt-1">Annonces Trouvées</div>
                    <Badge variant="outline" className="mt-2">
                      Données Réelles
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {prediction.listings.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Annonces Similaires</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {prediction.listings.slice(0, 5).map((listing, index) => (
                      <div key={index} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900">{listing.title}</h4>
                          <p className="text-lg font-semibold text-green-600">
                            {formatPrice(listing.price)} MAD
                          </p>
                        </div>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => window.open(listing.url, '_blank')}
                          className="ml-4"
                        >
                          <ExternalLink className="h-4 w-4 mr-1" />
                          Voir l'annonce
                        </Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
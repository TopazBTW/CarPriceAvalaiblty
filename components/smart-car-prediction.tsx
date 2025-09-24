"use client"

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { AlertCircle, TrendingUp, ExternalLink, Car, DollarSign, Sparkles } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  moroccanCarDatabase, 
  getModelsForBrand, 
  getYearsForModel, 
  getFuelTypesForModel,
  getTransmissionsForModel,
  getTypicalKilometersForModel,
  getPriceRangeForModel,
  getAllBrands
} from '@/lib/morocco-car-data'

interface CarPredictionRequest {
  Brand: string
  Model: string
  Year: number
  KM_Driven: number
  Fuel: string
  Seller_Type: string
  Transmission: string
  Owner: string
}

interface CarListing {
  title: string
  price: number
  url: string
}

interface PredictionResponse {
  predicted_price: number
  currency: string
  market_avg_price?: number
  listings: CarListing[]
  model_confidence: number
  scraping_source: string
}

const API_BASE_URL = 'http://localhost:8001'

const vehicleConditions = ['Neuf', 'Occasion']
const ownerTypes = ['First Owner'] // Simplifié - toujours First Owner par défaut

export function SmartCarPricePrediction() {
  const [formData, setFormData] = useState<CarPredictionRequest>({
    Brand: '',
    Model: '',
    Year: new Date().getFullYear() - 2,
    KM_Driven: 50000,
    Fuel: '',
    Seller_Type: 'Dealer', // Par défaut pour neuf/occasion
    Transmission: '',
    Owner: 'First Owner' // Toujours premier propriétaire par défaut
  })

  // États pour les options dynamiques
  const [availableModels, setAvailableModels] = useState<string[]>([])
  const [availableYears, setAvailableYears] = useState<number[]>([])
  const [availableFuels, setAvailableFuels] = useState<string[]>([])
  const [availableTransmissions, setAvailableTransmissions] = useState<string[]>([])
  const [suggestedKilometers, setSuggestedKilometers] = useState<number[]>([])
  const [priceRange, setPriceRange] = useState<[number, number]>([0, 0])

  const [prediction, setPrediction] = useState<PredictionResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Brands loaded from backend (authoritative) with local fallback
  const [remoteBrands, setRemoteBrands] = useState<string[] | null>(null)

  // Effet quand la marque change
  useEffect(() => {
    let mounted = true

    async function loadModelsForBrand(brand: string) {
      // Try backend first
      try {
        const res = await fetch(`${API_BASE_URL}/brands/${encodeURIComponent(brand)}/models`)
        if (res.ok) {
          const data = await res.json()
          const models = data.models.map((m: any) => m.model)
          if (mounted) setAvailableModels(models)
          return
        }
      } catch (e) {
        // fallback to local
      }

      // Local fallback
      const models = getModelsForBrand(brand)
      if (mounted) setAvailableModels(models)
    }

    if (formData.Brand) {
      loadModelsForBrand(formData.Brand)

      // Reset les champs dépendants
      setFormData(prev => ({
        ...prev,
        Model: '',
        Year: new Date().getFullYear() - 2,
        Fuel: '',
        Transmission: ''
      }))
      setAvailableYears([])
      setAvailableFuels([])
      setAvailableTransmissions([])
      setSuggestedKilometers([])
      setPriceRange([0, 0])
    } else {
      setAvailableModels([])
    }

    return () => { mounted = false }
  }, [formData.Brand])

  // Load remote brands on mount
  useEffect(() => {
    let mounted = true
    async function loadBrands() {
      try {
        const res = await fetch(`${API_BASE_URL}/brands`)
        if (res.ok) {
          const data = await res.json()
          if (mounted) setRemoteBrands(data.brands || [])
          return
        }
      } catch (e) {
        // ignore and fallback
      }

      // If backend not available, keep null so we use local
      if (mounted) setRemoteBrands(null)
    }

    loadBrands()
    return () => { mounted = false }
  }, [])

  // Effet quand le modèle change
  useEffect(() => {
    if (formData.Brand && formData.Model) {
      const years = getYearsForModel(formData.Brand, formData.Model)
      const fuels = getFuelTypesForModel(formData.Brand, formData.Model)
      const transmissions = getTransmissionsForModel(formData.Brand, formData.Model)
      const priceRange = getPriceRangeForModel(formData.Brand, formData.Model)
      
      setAvailableYears(years.sort((a, b) => b - a)) // Plus récent en premier
      setAvailableFuels(fuels)
      setAvailableTransmissions(transmissions)
      setPriceRange(priceRange)
      
      // Auto-sélection intelligente
      setFormData(prev => ({
        ...prev,
        Year: years[years.length - 1] || new Date().getFullYear() - 2, // Année la plus récente
        Fuel: fuels[0] || '', // Premier carburant disponible
        Transmission: transmissions.includes('Automatique') ? 'Automatique' : transmissions[0] || '', // Préférer automatique
        Seller_Type: 'Dealer', // Valeur par défaut
        Owner: 'First Owner' // Valeur par défaut
      }))
    }
  }, [formData.Brand, formData.Model])

  // Effet quand l'année change
  useEffect(() => {
    if (formData.Brand && formData.Model && formData.Year) {
      const kilometers = getTypicalKilometersForModel(formData.Brand, formData.Model, formData.Year)
      setSuggestedKilometers(kilometers.sort((a, b) => a - b))
      
      // Auto-sélection du kilométrage moyen
      const avgKm = kilometers[Math.floor(kilometers.length / 2)] || 50000
      setFormData(prev => ({
        ...prev,
        KM_Driven: avgKm
      }))
    }
  }, [formData.Brand, formData.Model, formData.Year])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setPrediction(null)

    try {
      // Validation
      const requiredFields = ['Brand', 'Model', 'Fuel', 'Transmission']
      for (const field of requiredFields) {
        if (!formData[field as keyof CarPredictionRequest]) {
          throw new Error(`Veuillez remplir le champ ${field}`)
        }
      }

      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      if (!response.ok) {
        const errorData = await response.text()
        throw new Error(`Erreur de prédiction: ${errorData}`)
      }

      const result: PredictionResponse = await response.json()
      setPrediction(result)

    } catch (err) {
      console.error('Prediction error:', err)
      setError(err instanceof Error ? err.message : 'Erreur lors de la prédiction du prix')
    } finally {
      setLoading(false)
    }
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('fr-MA', {
      style: 'decimal',
      minimumFractionDigits: 0
    }).format(price)
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4 flex items-center justify-center gap-2">
            <Sparkles className="h-8 w-8 text-blue-500" />
            Évaluation Intelligente de Voiture
          </h1>
          <p className="text-gray-600">
            Sélectionnez votre marque et laissez notre système intelligent vous guider automatiquement
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
                {/* Marque */}
                <div>
                  <label className="block text-sm font-medium mb-2">Marque *</label>
                  <Select value={formData.Brand || undefined} onValueChange={(value) => setFormData(prev => ({...prev, Brand: value}))}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Sélectionnez une marque" />
                    </SelectTrigger>
                    <SelectContent>
                      {(remoteBrands ?? getAllBrands()).map(brand => (
                        <SelectItem key={brand} value={brand}>{brand}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Modèle */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Modèle * 
                    {availableModels.length > 0 && (
                      <Badge variant="secondary" className="ml-2">
                        {availableModels.length} disponibles
                      </Badge>
                    )}
                  </label>
                  <Select 
                    value={formData.Model || undefined} 
                    onValueChange={(value) => setFormData(prev => ({...prev, Model: value}))}
                    disabled={!formData.Brand}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder={formData.Brand ? "Choisissez le modèle" : "Sélectionnez d'abord une marque"} />
                    </SelectTrigger>
                    <SelectContent>
                      {availableModels.map(model => (
                        <SelectItem key={model} value={model}>{model}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Année */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Année *
                    {availableYears.length > 0 && (
                      <Badge variant="secondary" className="ml-2">
                        {availableYears[0]} - {availableYears[availableYears.length - 1]}
                      </Badge>
                    )}
                  </label>
                  <Select 
                    value={formData.Year ? formData.Year.toString() : undefined} 
                    onValueChange={(value) => setFormData(prev => ({...prev, Year: parseInt(value)}))}
                    disabled={!formData.Model}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder={formData.Model ? "Année disponible" : "Sélectionnez le modèle d'abord"} />
                    </SelectTrigger>
                    <SelectContent>
                      {availableYears.map(year => (
                        <SelectItem key={year} value={year.toString()}>{year}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Kilométrage avec suggestions */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Kilométrage (km) *
                    {suggestedKilometers.length > 0 && (
                      <Badge variant="outline" className="ml-2">
                        Suggéré: {formatPrice(suggestedKilometers[Math.floor(suggestedKilometers.length / 2)])} km
                      </Badge>
                    )}
                  </label>
                  <div className="space-y-2">
                    <Input
                      type="number"
                      value={formData.KM_Driven}
                      onChange={(e) => setFormData(prev => ({...prev, KM_Driven: parseInt(e.target.value) || 0}))}
                      placeholder="Entrez le kilométrage"
                      min="0"
                      max="500000"
                    />
                    {suggestedKilometers.length > 0 && (
                      <div className="flex gap-2 flex-wrap">
                        {suggestedKilometers.slice(0, 3).map(km => (
                          <Button
                            key={km}
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => setFormData(prev => ({...prev, KM_Driven: km}))}
                          >
                            {formatPrice(km)} km
                          </Button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {/* Carburant */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Carburant *
                    {availableFuels.length > 0 && (
                      <Badge variant="secondary" className="ml-2">
                        {availableFuels.join(', ')}
                      </Badge>
                    )}
                  </label>
                  <Select 
                    value={formData.Fuel || undefined} 
                    onValueChange={(value) => setFormData(prev => ({...prev, Fuel: value}))}
                    disabled={!formData.Model}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder={formData.Model ? "Type de carburant" : "Sélectionnez le modèle d'abord"} />
                    </SelectTrigger>
                    <SelectContent>
                      {availableFuels.map(fuel => (
                        <SelectItem key={fuel} value={fuel}>{fuel}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Transmission */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Transmission *
                    {availableTransmissions.length > 0 && (
                      <Badge variant="secondary" className="ml-2">
                        {availableTransmissions.join(' / ')}
                      </Badge>
                    )}
                  </label>
                  <Select 
                    value={formData.Transmission || undefined} 
                    onValueChange={(value) => setFormData(prev => ({...prev, Transmission: value}))}
                    disabled={!formData.Model}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder={formData.Model ? "Type de transmission" : "Sélectionnez le modèle d'abord"} />
                    </SelectTrigger>
                    <SelectContent>
                      {availableTransmissions.map(transmission => (
                        <SelectItem key={transmission} value={transmission}>{transmission}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* État du véhicule */}
                <div>
                  <label className="block text-sm font-medium mb-2">État du véhicule *</label>
                  {/* Map internal Seller_Type ('Dealer'|'Individual') to the visible condition value ('Neuf'|'Occasion') */}
                  <Select
                    value={formData.Seller_Type === 'Dealer' ? 'Neuf' : 'Occasion'}
                    onValueChange={(value) => setFormData(prev => ({ ...prev, Seller_Type: value === 'Neuf' ? 'Dealer' : 'Individual' }))}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Neuf ou Occasion" />
                    </SelectTrigger>
                    <SelectContent>
                      {vehicleConditions.map(condition => (
                        <SelectItem key={condition} value={condition}>
                          {condition}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>


              </div>

              {/* Fourchette de prix estimée */}
              {priceRange[0] > 0 && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <DollarSign className="h-4 w-4 text-blue-500" />
                    <span className="text-sm font-medium text-blue-700">Fourchette de prix typique pour ce modèle</span>
                  </div>
                  <div className="text-lg font-bold text-blue-800">
                    {formatPrice(priceRange[0])} - {formatPrice(priceRange[1])} MAD
                  </div>
                </div>
              )}

              <Button 
                type="submit" 
                className="w-full" 
                size="lg"
                disabled={loading || !formData.Brand || !formData.Model}
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Analyse en cours...
                  </>
                ) : (
                  <>
                    <TrendingUp className="mr-2 h-4 w-4" />
                    Obtenir l'Évaluation
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Résultats */}
        {error && (
          <Alert className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {prediction && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-green-600" />
                Résultat de l'Évaluation
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-green-50 rounded-lg border border-green-200">
                  <div className="text-sm text-green-600 font-medium">Prix Estimé</div>
                  <div className="text-2xl font-bold text-green-800">
                    {formatPrice(prediction.predicted_price)} MAD
                  </div>
                </div>
                
                <div className="text-center p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="text-sm text-blue-600 font-medium">Confiance du Modèle</div>
                  <div className="text-2xl font-bold text-blue-800">
                    {Math.round(prediction.model_confidence * 100)}%
                  </div>
                </div>
                
                <div className="text-center p-4 bg-orange-50 rounded-lg border border-orange-200">
                  <div className="text-sm text-orange-600 font-medium">Source des Données</div>
                  <div className="text-lg font-bold text-orange-800 capitalize">
                    {prediction.scraping_source || 'ML Model'}
                  </div>
                </div>
              </div>

              {prediction.market_avg_price && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-600">Prix Moyen du Marché</div>
                  <div className="text-xl font-bold text-gray-800">
                    {formatPrice(prediction.market_avg_price)} MAD
                  </div>
                </div>
              )}

              {prediction.listings && prediction.listings.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-3">Annonces Similaires</h3>
                  <div className="space-y-3">
                    {prediction.listings.slice(0, 5).map((listing, index) => (
                      <div key={index} className="flex justify-between items-center p-3 border rounded-lg hover:bg-gray-50">
                        <div className="flex-1">
                          <div className="font-medium">{listing.title}</div>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="font-bold text-green-600">
                            {formatPrice(listing.price)} MAD
                          </span>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => window.open(listing.url, '_blank')}
                          >
                            <ExternalLink className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useState, useEffect } from "react"
import { Calculator, Loader2 } from "lucide-react"

export function HeroSection() {
  const [ownershipType, setOwnershipType] = useState("premiere")
  const [accidentHistory, setAccidentHistory] = useState("sans")
  
  // Form state
  const [brand, setBrand] = useState("")
  const [model, setModel] = useState("")
  const [year, setYear] = useState("")
  const [mileage, setMileage] = useState("")
  const [fuelType, setFuelType] = useState("")
  const [transmission, setTransmission] = useState("")
  const [city, setCity] = useState("")
  
  // API state
  const [brands, setBrands] = useState<string[]>([])
  const [models, setModels] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [prediction, setPrediction] = useState<any>(null)
  const [error, setError] = useState("")

  // Load brands on component mount
  useEffect(() => {
    const loadBrands = async () => {
      try {
        const res = await fetch('http://localhost:8000/brands')
        if (!res.ok) throw new Error('Failed to load brands')
        const data = await res.json()
        setBrands(data.brands || [])
      } catch (e) {
        console.error('Error loading brands:', e)
        setError('Failed to load brands')
      }
    }
    loadBrands()
  }, [])

  // Load models when brand changes
  useEffect(() => {
    if (!brand) {
      setModels([])
      setModel("")
      return
    }

    const loadModels = async () => {
      try {
        const encodedBrand = encodeURIComponent(brand)
        const res = await fetch(`http://localhost:8000/brands/${encodedBrand}/models`)
        if (!res.ok) throw new Error('Failed to load models')
        const data = await res.json()
        setModels(data.models?.map((m: any) => m.name || m) || [])
      } catch (e) {
        console.error('Error loading models:', e)
        setModels([])
      }
    }
    loadModels()
  }, [brand])

  // Handle prediction
  const handlePredict = async () => {
    if (!brand || !model || !year || !mileage || !fuelType || !transmission) {
      setError('Please fill in all required fields')
      return
    }

    setLoading(true)
    setError("")
    setPrediction(null)

    try {
      const ownerMap = {
        "premiere": "First Owner",
        "seconde": "Second Owner", 
        "troisieme": "Third Owner"
      }

      const response = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          brand: brand,
          model: model,
          year: parseInt(year),
          km_driven: parseInt(mileage),
          fuel_type: fuelType,
          transmission: transmission,
          seller_type: "Individual",
          owner: ownerMap[ownershipType as keyof typeof ownerMap]
        })
      })

      if (!response.ok) {
        throw new Error('Prediction failed')
      }

      const data = await response.json()
      setPrediction(data)
    } catch (e) {
      console.error('Prediction error:', e)
      setError('Failed to get price prediction. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="py-16 bg-gradient-to-b from-background to-muted/30">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-balance mb-6">Évaluation de Voitures d'Occasion</h1>
          <p className="text-lg text-muted-foreground text-balance max-w-2xl mx-auto">
            Obtenez une estimation précise et gratuite de votre véhicule en quelques minutes. Notre service utilise les
            données du marché marocain pour vous offrir la meilleure évaluation.
          </p>
        </div>

        <Card className="max-w-3xl mx-auto p-8 shadow-lg">
          <h2 className="text-2xl font-semibold mb-6 text-center">Calculateur de Prix de Voiture d'Occasion</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div>
              <label className="text-sm font-medium mb-2 block">Marque</label>
              <Select value={brand} onValueChange={setBrand}>
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionner la marque" />
                </SelectTrigger>
                <SelectContent>
                  {brands.map((brandName) => (
                    <SelectItem key={brandName} value={brandName}>{brandName}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>            <div>
              <label className="text-sm font-medium mb-2 block">Ville</label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionner la ville" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="casablanca">Casablanca</SelectItem>
                  <SelectItem value="rabat">Rabat</SelectItem>
                  <SelectItem value="marrakech">Marrakech</SelectItem>
                  <SelectItem value="fes">Fès</SelectItem>
                  <SelectItem value="tanger">Tanger</SelectItem>
                  <SelectItem value="agadir">Agadir</SelectItem>
                  <SelectItem value="meknes">Meknès</SelectItem>
                  <SelectItem value="oujda">Oujda</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Modèle</label>
              <Select value={model} onValueChange={setModel} disabled={!brand}>
                <SelectTrigger>
                  <SelectValue placeholder={!brand ? "Sélectionnez d'abord une marque" : "Sélectionner le modèle"} />
                </SelectTrigger>
                <SelectContent>
                  {models.map((modelName) => (
                    <SelectItem key={modelName} value={modelName}>{modelName}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div>
              <label className="text-sm font-medium mb-2 block">Kilométrage</label>
              <Input 
                placeholder="Ex: 50000" 
                type="number" 
                value={mileage}
                onChange={(e) => setMileage(e.target.value)}
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Année</label>
              <Select value={year} onValueChange={setYear}>
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionner l'année" />
                </SelectTrigger>
                <SelectContent>
                  {Array.from({ length: 25 }, (_, i) => 2024 - i).map((yearValue) => (
                    <SelectItem key={yearValue} value={yearValue.toString()}>
                      {yearValue}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="text-sm font-medium mb-2 block">Carburant</label>
              <Select value={fuelType} onValueChange={setFuelType}>
                <SelectTrigger>
                  <SelectValue placeholder="Type de carburant" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Petrol">Essence</SelectItem>
                  <SelectItem value="Diesel">Diesel</SelectItem>
                  <SelectItem value="Electric">Électrique</SelectItem>
                  <SelectItem value="Hybrid">Hybride</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Transmission</label>
              <Select value={transmission} onValueChange={setTransmission}>
                <SelectTrigger>
                  <SelectValue placeholder="Type de transmission" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Manual">Manuelle</SelectItem>
                  <SelectItem value="Automatic">Automatique</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-6 mb-8">
            <div>
              <label className="text-sm font-medium mb-3 block">Type de propriétaire</label>
              <Tabs value={ownershipType} onValueChange={setOwnershipType} className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="premiere">Première main</TabsTrigger>
                  <TabsTrigger value="seconde">Seconde main</TabsTrigger>
                  <TabsTrigger value="troisieme">Troisième main</TabsTrigger>
                </TabsList>
              </Tabs>
            </div>

            <div>
              <label className="text-sm font-medium mb-3 block">Historique d'accidents</label>
              <Tabs value={accidentHistory} onValueChange={setAccidentHistory} className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="sans">Pas de sinistre</TabsTrigger>
                  <TabsTrigger value="avec">Avec sinistre</TabsTrigger>
                </TabsList>
              </Tabs>
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}

          {prediction && (
            <div className="bg-green-50 border border-green-200 rounded-md p-6 mb-4">
              <h3 className="text-lg font-semibold text-green-800 mb-2">Estimation de Prix</h3>
              <div className="space-y-2">
                <p className="text-2xl font-bold text-green-600">
                  {Math.round(prediction.predicted_price).toLocaleString()} MAD
                </p>
                <p className="text-sm text-green-700">
                  Confiance: {Math.round(prediction.confidence * 100)}%
                </p>
              </div>
            </div>
          )}

          <Button 
            className="w-full bg-primary hover:bg-primary/90 text-primary-foreground py-3 text-lg font-medium"
            onClick={handlePredict}
            disabled={loading}
          >
            {loading ? (
              <>
                <div className="mr-2 h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
                Calcul en cours...
              </>
            ) : (
              <>
                <Calculator className="mr-2 h-5 w-5" />
                Obtenir l'Évaluation
              </>
            )}
          </Button>
        </Card>
      </div>
    </section>
  )
}

"use client"

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Search, Car, DollarSign, Award, Filter, Grid3X3 } from 'lucide-react'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

interface PriceRange {
  label: string
  min: number
  max: number
}

interface CarResult {
  brand: string
  model: string
  title: string
  price: number
  url: string
  year?: number
  image?: string
}

interface BrandCategories {
  premium: string[]
  generaliste: string[]
  electric: string[]
  chinese: string[]
}

export default function KifalStyleCarSearch() {
  const [searchParams, setSearchParams] = useState({
    marque: '',
    modele: '',
    type: '',
    min_prix: '',
    max_prix: ''
  })
  
  const [searchResults, setSearchResults] = useState<CarResult[]>([])
  const [priceRanges, setPriceRanges] = useState<PriceRange[]>([])
  const [bodyTypes, setBodyTypes] = useState<string[]>([])
  const [brandCategories, setBrandCategories] = useState<BrandCategories>({
    premium: [],
    generaliste: [],
    electric: [],
    chinese: []
  })
  const [popularModels, setPopularModels] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedPriceRange, setSelectedPriceRange] = useState('')

  useEffect(() => {
    loadInitialData()
  }, [])

  const loadInitialData = async () => {
    try {
      // Load price ranges
      const priceRes = await fetch(`${API_BASE_URL}/kifal/price-ranges`)
      if (priceRes.ok) {
        setPriceRanges(await priceRes.json())
      }

      // Load body types
      const bodyRes = await fetch(`${API_BASE_URL}/kifal/body-types`)
      if (bodyRes.ok) {
        setBodyTypes(await bodyRes.json())
      }

      // Load brand categories
      const brandsRes = await fetch(`${API_BASE_URL}/kifal/brands`)
      if (brandsRes.ok) {
        setBrandCategories(await brandsRes.json())
      }

      // Load popular models
      const popularRes = await fetch(`${API_BASE_URL}/kifal/popular`)
      if (popularRes.ok) {
        setPopularModels(await popularRes.json())
      }
    } catch (error) {
      console.error('Error loading data:', error)
    }
  }

  const handleSearch = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      Object.entries(searchParams).forEach(([key, value]) => {
        if (value) params.append(key, value)
      })

      const response = await fetch(`${API_BASE_URL}/kifal/search?${params}`)
      if (response.ok) {
        const data = await response.json()
        setSearchResults(data.results)
      }
    } catch (error) {
      console.error('Search error:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePriceRangeSearch = async (range: PriceRange) => {
    setLoading(true)
    setSelectedPriceRange(range.label)
    try {
      const response = await fetch(`${API_BASE_URL}/kifal/price-range/${encodeURIComponent(range.label)}`)
      if (response.ok) {
        const data = await response.json()
        setSearchResults(data.cars)
      }
    } catch (error) {
      console.error('Price range search error:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatPrice = (price: number) => {
    return `${(price / 1000).toFixed(0)}K DH`
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            🚗 Voitures neuves à vendre au Maroc
          </h1>
          <p className="text-gray-600">
            Découvrez les derniers modèles et les meilleures offres sur les voitures disponibles sur le marché marocain.
          </p>
        </div>
      </div>

      {/* Search Section */}
      <div className="container mx-auto px-4 py-8">
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Search className="w-5 h-5" />
              Recherche Avancée
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              <Select onValueChange={(value) => setSearchParams(prev => ({ ...prev, marque: value }))}>
                <SelectTrigger>
                  <SelectValue placeholder="Marque" />
                </SelectTrigger>
                <SelectContent>
                  {Object.values(brandCategories).flat().map(brand => (
                    <SelectItem key={brand} value={brand}>{brand}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Input
                placeholder="Modèle"
                value={searchParams.modele}
                onChange={(e) => setSearchParams(prev => ({ ...prev, modele: e.target.value }))}
              />

              <Select onValueChange={(value) => setSearchParams(prev => ({ ...prev, type: value }))}>
                <SelectTrigger>
                  <SelectValue placeholder="Type de carrosserie" />
                </SelectTrigger>
                <SelectContent>
                  {bodyTypes.map(type => (
                    <SelectItem key={type} value={type}>{type}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Input
                type="number"
                placeholder="Prix min (DH)"
                value={searchParams.min_prix}
                onChange={(e) => setSearchParams(prev => ({ ...prev, min_prix: e.target.value }))}
              />

              <Button onClick={handleSearch} disabled={loading} className="w-full">
                {loading ? 'Recherche...' : 'Rechercher'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Brand Categories */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Premium Brands */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Award className="w-5 h-5 text-yellow-500" />
                Marques Premium
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-4 gap-4">
                {brandCategories.premium.map(brand => (
                  <Button
                    key={brand}
                    variant="outline"
                    className="h-16 flex flex-col items-center justify-center"
                    onClick={() => setSearchParams(prev => ({ ...prev, marque: brand }))}
                  >
                    <img 
                      src={`https://referentiel.kifal.ma/imgs/brands/${brand}.webp`}
                      alt={brand}
                      className="w-8 h-8 mb-1"
                      onError={(e) => {
                        e.currentTarget.style.display = 'none'
                      }}
                    />
                    <span className="text-xs">{brand}</span>
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* General Brands */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Car className="w-5 h-5 text-blue-500" />
                Marques Généralistes
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-4 gap-4">
                {brandCategories.generaliste.map(brand => (
                  <Button
                    key={brand}
                    variant="outline"
                    className="h-16 flex flex-col items-center justify-center"
                    onClick={() => setSearchParams(prev => ({ ...prev, marque: brand }))}
                  >
                    <img 
                      src={`https://referentiel.kifal.ma/imgs/brands/${brand}.webp`}
                      alt={brand}
                      className="w-8 h-8 mb-1"
                      onError={(e) => {
                        e.currentTarget.style.display = 'none'
                      }}
                    />
                    <span className="text-xs">{brand}</span>
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Price Range Categories */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-green-500" />
              Voitures les mieux notées par prix
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {priceRanges.map(range => (
                <Button
                  key={range.label}
                  variant={selectedPriceRange === range.label ? "default" : "outline"}
                  className="h-20 flex flex-col items-center justify-center"
                  onClick={() => handlePriceRangeSearch(range)}
                >
                  <DollarSign className="w-4 h-4 mb-1" />
                  <span className="text-xs text-center">{range.label}</span>
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Search Results */}
        {searchResults.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>
                Résultats de recherche ({searchResults.length} voitures)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {searchResults.map((car, index) => (
                  <Card key={index} className="hover:shadow-lg transition-shadow cursor-pointer">
                    <CardContent className="p-4">
                      <div className="aspect-video bg-gray-100 rounded-lg mb-3 flex items-center justify-center">
                        <Car className="w-8 h-8 text-gray-400" />
                      </div>
                      <h3 className="font-semibold text-sm mb-2 line-clamp-2">
                        {car.title}
                      </h3>
                      <div className="flex justify-between items-center">
                        <Badge variant="secondary" className="text-xs">
                          {car.brand}
                        </Badge>
                        <span className="font-bold text-green-600">
                          {formatPrice(car.price)}
                        </span>
                      </div>
                      {car.year && (
                        <p className="text-xs text-gray-500 mt-1">Année: {car.year}</p>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Popular Models */}
        {popularModels.length > 0 && (
          <Card className="mt-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Grid3X3 className="w-5 h-5 text-purple-500" />
                Top Modèles
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {popularModels.slice(0, 10).map((model, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    className="h-16 flex flex-col items-center justify-center"
                    onClick={() => setSearchParams(prev => ({ 
                      ...prev, 
                      marque: model.brand,
                      modele: model.model 
                    }))}
                  >
                    <span className="text-xs font-semibold">{model.model}</span>
                    <span className="text-xs text-gray-500">
                      {formatPrice(model.avg_price)}
                    </span>
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
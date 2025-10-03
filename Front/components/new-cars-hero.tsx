"use client"

import { useState, useEffect } from "react"
import { Search, Camera, Car } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card } from "@/components/ui/card"

export function NewCarsHero() {
  const [searchType, setSearchType] = useState("brand")

  const [brands, setBrands] = useState<string[]>([])
  const [models, setModels] = useState<string[]>([])
  const [selectedBrand, setSelectedBrand] = useState<string | undefined>(undefined)
  const [selectedModel, setSelectedModel] = useState<string | undefined>(undefined)
  const [loadingBrands, setLoadingBrands] = useState(false)
  const [loadingModels, setLoadingModels] = useState(false)

  useEffect(() => {
    // Load brands from backend on mount
    const loadBrands = async () => {
      try {
        setLoadingBrands(true)
        const res = await fetch('http://localhost:8000/brands')
        if (!res.ok) throw new Error('Failed to load brands')
        const data = await res.json()
        // backend returns { brands: [...] }
        const names: string[] = (data.brands || []).map((b: any) => b.name || b)
        setBrands(names)
      } catch (e) {
        console.error('Error fetching brands', e)
      } finally {
        setLoadingBrands(false)
      }
    }

    loadBrands()
  }, [])

  useEffect(() => {
    // When brand changes, fetch models for that brand
    if (!selectedBrand) {
      setModels([])
      setSelectedModel(undefined)
      return
    }

    const loadModels = async () => {
      try {
        setLoadingModels(true)
        const encoded = encodeURIComponent(selectedBrand)
        const res = await fetch(`http://localhost:8000/brands/${encoded}/models`)
        if (!res.ok) throw new Error('Failed to load models')
        const data = await res.json()
        // backend returns { models: [ { name: '...' }, ... ] }
        const names: string[] = (data.models || []).map((m: any) => m.name || m)
        setModels(names)
      } catch (e) {
        console.error('Error fetching models', e)
        setModels([])
      } finally {
        setLoadingModels(false)
      }
    }

    loadModels()
  }, [selectedBrand])

  return (
    <section className="py-16 bg-gradient-to-b from-background to-muted/30">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Car className="h-10 w-10 text-primary" />
            <h1 className="text-4xl md:text-5xl font-bold text-balance">Voitures Neuves à Vendre au Maroc</h1>
          </div>
          <p className="text-lg text-muted-foreground text-balance max-w-2xl mx-auto">
            Découvrez les derniers modèles de voitures neuves disponibles au Maroc avec les meilleurs prix et
            financements.
          </p>
        </div>

        <Card className="max-w-3xl mx-auto p-8 shadow-lg">
          <h2 className="text-2xl font-semibold mb-6 text-center">Rechercher une Voiture Neuve</h2>

          <Tabs value={searchType} onValueChange={setSearchType} className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-6">
              <TabsTrigger value="brand">Par marque/modèle</TabsTrigger>
              <TabsTrigger value="bodytype">Par type de carrosserie</TabsTrigger>
            </TabsList>

            <TabsContent value="brand" className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="brand">Marque</Label>
                  <Select value={selectedBrand} onValueChange={(v) => setSelectedBrand(v || undefined)}>
                    <SelectTrigger id="brand">
                      <SelectValue placeholder={loadingBrands ? 'Chargement...' : 'Sélectionner une marque'} />
                    </SelectTrigger>
                    <SelectContent>
                      {brands.map((brand) => (
                        <SelectItem key={brand} value={brand}>
                          {brand}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="model">Modèle</Label>
                  <Select
                    value={selectedModel}
                    onValueChange={(v) => {
                      // Don't set special placeholder values
                      if (v === "no-brand" || v === "no-models") return
                      setSelectedModel(v || undefined)
                    }}
                  >
                    <SelectTrigger id="model" aria-disabled={!selectedBrand}>
                      <SelectValue placeholder={
                        !selectedBrand ? 'Choisissez d’abord une marque' : loadingModels ? 'Chargement...' : 'Sélectionner un modèle'
                      } />
                    </SelectTrigger>
                    <SelectContent>
                      {!selectedBrand && <SelectItem value="no-brand">-- Aucun --</SelectItem>}
                      {models.length === 0 && selectedBrand && !loadingModels && (
                        <SelectItem value="no-models" disabled>Aucun modèle trouvé</SelectItem>
                      )}
                      {models.map((model) => (
                        <SelectItem key={model} value={model}>
                          {model}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-3 pt-4">
                <Button
                  className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground py-3 text-lg font-medium"
                  onClick={async () => {
                    try {
                      const params = new URLSearchParams()
                      if (selectedBrand) params.append('brand', selectedBrand)
                      if (selectedModel) params.append('q', selectedModel)
                      params.append('limit', '50')

                      const res = await fetch(`http://localhost:8000/search?${params.toString()}`)
                      if (!res.ok) throw new Error('Search failed')
                      const data = await res.json()
                      console.log('Search results', data)
                      // TODO: navigate to results page or display results in UI
                    } catch (e) {
                      console.error('Search error', e)
                    }
                  }}
                >
                  <Search className="mr-2 h-5 w-5" />
                  Rechercher
                </Button>
                <Button variant="outline" className="flex-1 py-3 text-lg font-medium bg-transparent">
                  <Camera className="mr-2 h-5 w-5" />
                  Par Image
                </Button>
              </div>
            </TabsContent>

            <TabsContent value="bodytype" className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="bodytype">Type de carrosserie</Label>
                <Select>
                  <SelectTrigger id="bodytype">
                    <SelectValue placeholder="Sélectionner un type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="berline">Berline</SelectItem>
                    <SelectItem value="suv">SUV</SelectItem>
                    <SelectItem value="citadine">Citadine</SelectItem>
                    <SelectItem value="compacte">Compacte</SelectItem>
                    <SelectItem value="coupe">Coupé</SelectItem>
                    <SelectItem value="crossover">Crossover</SelectItem>
                    <SelectItem value="monospace">Monospace</SelectItem>
                    <SelectItem value="pickup">Pick-up</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex flex-col sm:flex-row gap-3 pt-4">
                <Button className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground py-3 text-lg font-medium">
                  <Search className="mr-2 h-5 w-5" />
                  Rechercher
                </Button>
                <Button variant="outline" className="flex-1 py-3 text-lg font-medium bg-transparent">
                  <Camera className="mr-2 h-5 w-5" />
                  Par Image
                </Button>
              </div>
            </TabsContent>
          </Tabs>
        </Card>
      </div>
    </section>
  )
}

"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useState } from "react"

export function HeroSection() {
  const [ownershipType, setOwnershipType] = useState("premiere")
  const [accidentHistory, setAccidentHistory] = useState("sans")

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
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionner la marque" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="toyota">Toyota</SelectItem>
                  <SelectItem value="renault">Renault</SelectItem>
                  <SelectItem value="peugeot">Peugeot</SelectItem>
                  <SelectItem value="dacia">Dacia</SelectItem>
                  <SelectItem value="hyundai">Hyundai</SelectItem>
                  <SelectItem value="kia">Kia</SelectItem>
                  <SelectItem value="volkswagen">Volkswagen</SelectItem>
                  <SelectItem value="ford">Ford</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
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
              <Input placeholder="Ex: Clio, Logan..." />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div>
              <label className="text-sm font-medium mb-2 block">Kilométrage</label>
              <Input placeholder="Ex: 50000" type="number" />
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Année</label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionner l'année" />
                </SelectTrigger>
                <SelectContent>
                  {Array.from({ length: 25 }, (_, i) => 2024 - i).map((year) => (
                    <SelectItem key={year} value={year.toString()}>
                      {year}
                    </SelectItem>
                  ))}
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

          <Button className="w-full bg-primary hover:bg-primary/90 text-primary-foreground py-3 text-lg font-medium">
            Obtenir l'Évaluation
          </Button>
        </Card>
      </div>
    </section>
  )
}

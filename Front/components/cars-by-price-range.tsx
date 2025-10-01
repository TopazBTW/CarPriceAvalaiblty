"use client"

import { Button } from "@/components/ui/button"
import { ChevronRight } from "lucide-react"

export function CarsByPriceRange() {
  const priceRanges = [
    {
      range: "moins de 200K DH",
      cars: [
        {
          brand: "DACIA",
          model: "DACIA DUSTER",
          variant: "Modèle 4 Roues",
          price: "RENAULT 249",
          image: "/dacia-duster-suv.jpg",
          link: "Acheter les voitures moins de 200K DH",
        },
      ],
    },
    {
      range: "200K - 300K DH",
      cars: [
        {
          brand: "SKODA",
          model: "SKODA SUPERB",
          variant: "Modèle Hybride",
          price: "TOYOTA Série Grise",
          image: "/skoda-superb-sedan.jpg",
          link: "Acheter les voitures 200K-300K DH",
        },
      ],
    },
    {
      range: "300K - 400K DH",
      cars: [
        {
          brand: "TOYOTA",
          model: "TOYOTA C-HR",
          variant: "Modèle Compacte",
          price: "SUV II",
          image: "/toyota-chr-crossover.jpg",
          link: "Acheter les voitures 300K-400K DH",
        },
      ],
    },
    {
      range: "400K - 600K DH",
      cars: [
        {
          brand: "AUDI",
          model: "AUDI SUV",
          variant: "AUDI SQ",
          price: "BMW Série 4",
          image: "/audi-suv-luxury.jpg",
          link: "Acheter les voitures 400K-600K DH",
        },
      ],
    },
    {
      range: "600K - 800K DH",
      cars: [
        {
          brand: "BMW",
          model: "BMW SUV",
          variant: "PORSCHE Macan",
          price: "Modèle Cabriolet",
          image: "/bmw-suv-luxury.jpg",
          link: "Acheter les voitures 600K-800K DH",
        },
      ],
    },
    {
      range: "Plus de 800K DH",
      cars: [
        {
          brand: "MERCEDES",
          model: "Modèle Berline",
          variant: "MERCEDES-BENZ Classe E",
          price: "Modèle SUV",
          image: "/mercedes-benz-luxury-sedan.jpg",
          link: "Acheter les voitures Plus de 800K DH",
        },
      ],
    },
  ]

  return (
    <section className="py-16 bg-muted/30">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold text-center mb-12">Voitures les mieux notées par prix</h2>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {priceRanges.map((range, index) => (
            <div key={index} className="space-y-4">
              <h3 className="font-semibold text-lg text-primary">{range.range}</h3>
              {range.cars.map((car, carIndex) => (
                <div
                  key={carIndex}
                  className="bg-card rounded-lg overflow-hidden border border-border hover:shadow-lg transition-shadow"
                >
                  <img
                    src={car.image || "/placeholder.svg"}
                    alt={`${car.brand} ${car.model}`}
                    className="w-full h-48 object-cover"
                  />
                  <div className="p-4 space-y-2">
                    <div className="text-xs text-muted-foreground">{car.brand}</div>
                    <h4 className="font-semibold">{car.model}</h4>
                    <div className="text-sm text-muted-foreground">{car.variant}</div>
                    <div className="text-sm text-muted-foreground">{car.price}</div>
                    <Button variant="link" className="p-0 h-auto text-primary">
                      {car.link}
                      <ChevronRight className="ml-1 h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

"use client"

import { Button } from "@/components/ui/button"
import { ChevronDown } from "lucide-react"

export function CarBrandsGrid() {
  const brands = [
    { name: "Dacia", logo: "/dacia-logo.jpg" },
    { name: "Renault", logo: "/renault-logo.jpg" },
    { name: "Peugeot", logo: "/peugeot-logo.jpg" },
    { name: "Citroën", logo: "/citroen-logo.jpg" },
    { name: "BMW", logo: "/bmw-logo.png" },
    { name: "Opel", logo: "/opel-logo.jpg" },
    { name: "Fiat", logo: "/fiat-logo.png" },
    { name: "Seat", logo: "/generic-car-logo.png" },
    { name: "Hyundai", logo: "/hyundai-logo.png" },
    { name: "Kia", logo: "/kia-logo.png" },
    { name: "Peugeot", logo: "/peugeot-logo.jpg" },
    { name: "Volkswagen", logo: "/volkswagen-logo.png" },
    { name: "Ford", logo: "/ford-logo-generic.png" },
    { name: "Toyota", logo: "/toyota-logo.png" },
    { name: "Nissan", logo: "/nissan-logo.png" },
    { name: "Mazda", logo: "/mazda-logo.jpg" },
  ]

  return (
    <section className="py-16 bg-background">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold text-center mb-12">Marques de voitures neuves vendues au maroc</h2>

        <div className="grid grid-cols-4 md:grid-cols-8 gap-4 mb-8">
          {brands.map((brand, index) => (
            <button
              key={index}
              className="flex flex-col items-center justify-center p-4 bg-card hover:bg-accent rounded-lg transition-colors border border-border"
            >
              <img src={brand.logo || "/placeholder.svg"} alt={brand.name} className="h-12 w-12 object-contain mb-2" />
              <span className="text-xs text-center">{brand.name}</span>
            </button>
          ))}
        </div>

        <div className="text-center">
          <Button variant="outline" size="lg">
            Afficher plus
            <ChevronDown className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </div>
    </section>
  )
}

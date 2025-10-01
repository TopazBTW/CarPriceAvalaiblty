"use client"

import { Button } from "@/components/ui/button"
import { ChevronDown } from "lucide-react"

export function BodyTypeCategories() {
  const bodyTypes = [
    { name: "Berline", image: "/silver-sedan.png" },
    { name: "Cabriolet / Roadster", image: "/classic-red-convertible.png" },
    { name: "Citadine", image: "/city-car.jpg" },
    { name: "Compacte", image: "/compact-car-city.png" },
    { name: "Coupé", image: "/sleek-red-coupe.png" },
    { name: "Crossover", image: "/crossover-suv.jpg" },
    { name: "Familiale / Cabrio", image: "/station-wagon.jpg" },
    { name: "Ludospace/Utilitaire léger", image: "/van-vehicle.jpg" },
    { name: "Monospace", image: "/family-road-trip-minivan.png" },
    { name: "Monospace / Break", image: "/mpv-car.jpg" },
    { name: "Pick-up", image: "/classic-red-pickup.png" },
  ]

  return (
    <section className="py-16 bg-background">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mb-8">
          {bodyTypes.map((type, index) => (
            <button
              key={index}
              className="flex flex-col items-center p-6 bg-card hover:bg-accent rounded-lg transition-colors border border-border group"
            >
              <img src={type.image || "/placeholder.svg"} alt={type.name} className="h-24 w-full object-contain mb-4" />
              <span className="text-sm font-medium text-center group-hover:text-primary transition-colors">
                {type.name}
              </span>
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

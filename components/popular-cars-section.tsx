import { Card, CardContent } from "@/components/ui/card"

export function PopularCarsSection() {
  const popularCars = [
    {
      name: "Dacia Logan",
      priceRange: "85 000 - 120 000 DH",
      image: "/dacia-logan-sedan-car.jpg",
    },
    {
      name: "Renault Clio",
      priceRange: "95 000 - 140 000 DH",
      image: "/renault-clio-hatchback-car.jpg",
    },
    {
      name: "Toyota Yaris",
      priceRange: "110 000 - 160 000 DH",
      image: "/toyota-yaris-compact-car.jpg",
    },
  ]

  return (
    <section className="py-16 bg-muted/30">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">Voitures d'Occasion Populaires</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {popularCars.map((car) => (
            <Card key={car.name} className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="aspect-video bg-muted">
                <img src={car.image || "/placeholder.svg"} alt={car.name} className="w-full h-full object-cover" />
              </div>
              <CardContent className="p-4">
                <h3 className="font-semibold text-lg mb-2">{car.name}</h3>
                <p className="text-primary font-medium">{car.priceRange}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}

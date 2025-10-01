import {
  Building2,
  Landmark,
  MSquare as Mosque,
  Pause as Vase,
  Sailboat,
  Palmtree,
  Castle,
  Mountain,
  MapPin,
} from "lucide-react"

export function CitiesSection() {
  const cities = [
    { name: "Casablanca", icon: Building2 },
    { name: "Rabat", icon: Landmark },
    { name: "Marrakech", icon: Mosque },
    { name: "Fès", icon: Vase },
    { name: "Tanger", icon: Sailboat },
    { name: "Agadir", icon: Palmtree },
    { name: "Meknès", icon: Castle },
    { name: "Oujda", icon: Mountain },
    { name: "Tétouan", icon: Mountain },
    { name: "Salé", icon: MapPin },
    { name: "Kénitra", icon: MapPin },
    { name: "El Jadida", icon: Castle },
  ]

  return (
    <section className="py-16">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">Voitures d'Occasion par Ville</h2>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 max-w-5xl mx-auto">
          {cities.map((city) => {
            const Icon = city.icon
            return (
              <div
                key={city.name}
                className="text-center p-4 rounded-lg hover:bg-muted/50 transition-colors cursor-pointer group"
              >
                <div className="flex items-center justify-center mb-2">
                  <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                    <Icon className="h-6 w-6 text-primary" />
                  </div>
                </div>
                <h3 className="font-medium text-sm">{city.name}</h3>
              </div>
            )
          })}
        </div>

        <div className="text-center mt-8">
          <button className="text-primary hover:underline font-medium">Voir Plus de Villes</button>
        </div>
      </div>
    </section>
  )
}

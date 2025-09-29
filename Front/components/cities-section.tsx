export function CitiesSection() {
  const cities = [
    { name: "Casablanca", icon: "🏢" },
    { name: "Rabat", icon: "🏛️" },
    { name: "Marrakech", icon: "🕌" },
    { name: "Fès", icon: "🏺" },
    { name: "Tanger", icon: "⛵" },
    { name: "Agadir", icon: "🏖️" },
    { name: "Meknès", icon: "🏰" },
    { name: "Oujda", icon: "🌄" },
    { name: "Tétouan", icon: "🏔️" },
    { name: "Salé", icon: "🌊" },
    { name: "Kénitra", icon: "🌾" },
    { name: "El Jadida", icon: "🏰" },
  ]

  return (
    <section className="py-16">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">Voitures d'Occasion par Ville</h2>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 max-w-5xl mx-auto">
          {cities.map((city) => (
            <div
              key={city.name}
              className="text-center p-4 rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
            >
              <div className="text-3xl mb-2">{city.icon}</div>
              <h3 className="font-medium text-sm">{city.name}</h3>
            </div>
          ))}
        </div>

        <div className="text-center mt-8">
          <button className="text-primary hover:underline font-medium">Voir Plus de Villes</button>
        </div>
      </div>
    </section>
  )
}

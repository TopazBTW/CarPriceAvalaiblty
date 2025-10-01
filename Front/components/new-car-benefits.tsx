import { ShieldCheck, Sparkles, Wallet } from "lucide-react"

export function NewCarBenefits() {
  const benefits = [
    {
      icon: Sparkles,
      title: "Technologie de Pointe",
      description:
        "Les nouvelles voitures sont équipées de la dernière technologie embarquée qui améliore l'efficacité énergétique et permet à votre véhicule de rouler à long terme.",
    },
    {
      icon: ShieldCheck,
      title: "Garantie du Fabricant",
      description:
        "Les voitures neuves sont livrées avec une garantie constructeur. Si quelque chose ne va pas, vous n'avez pas à vous soucier de payer pour les réparations.",
    },
    {
      icon: Wallet,
      title: "Options de Financement",
      description:
        "Le crédit des voitures neuves permet aux acheteurs de payer leur véhicule en plusieurs versements, rendant l'achat plus abordable.",
    },
  ]

  return (
    <section className="py-16 bg-muted/30">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">Pourquoi Acheter une Voiture Neuve?</h2>
          <p className="text-muted-foreground max-w-3xl mx-auto text-balance">
            Acheter une voiture neuve présente de nombreux avantages pour les conducteurs marocains.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          {benefits.map((benefit, index) => (
            <div key={index} className="text-center">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <benefit.icon className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">{benefit.title}</h3>
              <p className="text-muted-foreground text-sm">{benefit.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

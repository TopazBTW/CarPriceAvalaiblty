import { Gauge, ShieldCheck, Database } from "lucide-react"

export function FeaturesSection() {
  return (
    <section className="py-16 bg-muted/30">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">Qu'est-ce qu'AutoValue?</h2>
          <p className="text-muted-foreground max-w-3xl mx-auto text-balance">
            AutoValue est un service d'évaluation de voitures d'occasion qui utilise des algorithmes avancés pour
            déterminer avec précision la valeur de votre véhicule basée sur les données du marché marocain.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          <div className="text-center">
            <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <Gauge className="h-8 w-8 text-primary" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Rapidité</h3>
            <p className="text-muted-foreground text-sm">
              Obtenez votre évaluation en moins de 2 minutes avec notre système automatisé.
            </p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <ShieldCheck className="h-8 w-8 text-primary" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Précision</h3>
            <p className="text-muted-foreground text-sm">
              Nos données sont mises à jour quotidiennement avec les prix du marché marocain.
            </p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <Database className="h-8 w-8 text-primary" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Couverture</h3>
            <p className="text-muted-foreground text-sm">
              AutoValue couvre toutes les grandes marques et modèles disponibles au Maroc.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}

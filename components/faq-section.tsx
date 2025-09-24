import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"

export function FAQSection() {
  return (
    <section className="py-16">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">Questions Fréquentes</h2>
        </div>

        <div className="max-w-3xl mx-auto">
          <Accordion type="single" collapsible>
            <AccordionItem value="item-1">
              <AccordionTrigger>Qu'est-ce que l'Évaluation de Voiture d'Occasion?</AccordionTrigger>
              <AccordionContent>
                L'évaluation de voiture d'occasion est un processus qui détermine la valeur marchande actuelle de votre
                véhicule. Notre service utilise les données du marché marocain, l'état du véhicule, le kilométrage et
                d'autres facteurs pour fournir une estimation précise.
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="item-2">
              <AccordionTrigger>
                Pourquoi AutoValue est-il le meilleur site pour l'Évaluation de Voitures d'Occasion?
              </AccordionTrigger>
              <AccordionContent>
                AutoValue utilise des algorithmes avancés et des données en temps réel du marché automobile marocain.
                Notre plateforme est mise à jour quotidiennement et prend en compte les spécificités du marché local
                pour vous offrir l'évaluation la plus précise possible.
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="item-3">
              <AccordionTrigger>
                Dois-je payer ou m'inscrire pour utiliser l'Évaluation de Voiture d'Occasion?
              </AccordionTrigger>
              <AccordionContent>
                Non, notre service d'évaluation de base est entièrement gratuit. Vous n'avez pas besoin de créer un
                compte pour obtenir une estimation de votre véhicule.
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="item-4">
              <AccordionTrigger>
                Quelles sont les villes populaires pour acheter une voiture d'occasion?
              </AccordionTrigger>
              <AccordionContent>
                Les principales villes pour l'achat de voitures d'occasion au Maroc incluent Casablanca, Rabat,
                Marrakech, Fès, Tanger, et Agadir. Ces villes offrent le plus grand choix de véhicules et les meilleurs
                prix du marché.
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </div>
      </div>
    </section>
  )
}

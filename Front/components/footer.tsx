import { Facebook, Twitter, Instagram, Youtube, Mail, Phone, MapPin } from "lucide-react"

export function Footer() {
  return (
    <footer className="bg-primary text-primary-foreground">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <div className="h-8 w-8 bg-primary-foreground rounded-md flex items-center justify-center">
                <span className="text-primary font-bold text-sm">AV</span>
              </div>
              <span className="font-semibold text-lg">AutoValue</span>
            </div>
            <p className="text-primary-foreground/80 text-sm mb-4">
              Votre partenaire de confiance pour l'évaluation de voitures d'occasion au Maroc.
            </p>
            <div className="space-y-2 mb-4 text-sm text-primary-foreground/80">
              <div className="flex items-center gap-2">
                <Phone className="h-4 w-4" />
                <span>+212 5XX-XXXXXX</span>
              </div>
              <div className="flex items-center gap-2">
                <Mail className="h-4 w-4" />
                <span>contact@autovalue.ma</span>
              </div>
              <div className="flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                <span>Casablanca, Maroc</span>
              </div>
            </div>
            <div className="flex space-x-4">
              <a href="#" className="hover:text-primary-foreground/60 transition-colors">
                <Facebook className="h-5 w-5" />
              </a>
              <a href="#" className="hover:text-primary-foreground/60 transition-colors">
                <Twitter className="h-5 w-5" />
              </a>
              <a href="#" className="hover:text-primary-foreground/60 transition-colors">
                <Instagram className="h-5 w-5" />
              </a>
              <a href="#" className="hover:text-primary-foreground/60 transition-colors">
                <Youtube className="h-5 w-5" />
              </a>
            </div>
          </div>

          <div>
            <h3 className="font-semibold mb-4">À Propos</h3>
            <ul className="space-y-2 text-sm text-primary-foreground/80">
              <li>
                <a href="#" className="hover:text-primary-foreground">
                  Qui sommes-nous
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary-foreground">
                  Carrières
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary-foreground">
                  Presse
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary-foreground">
                  Partenaires
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold mb-4">Services</h3>
            <ul className="space-y-2 text-sm text-primary-foreground/80">
              <li>
                <a href="#" className="hover:text-primary-foreground">
                  Évaluation Gratuite
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary-foreground">
                  Vendre ma Voiture
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary-foreground">
                  Acheter une Voiture
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary-foreground">
                  Financement
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold mb-4">Support</h3>
            <ul className="space-y-2 text-sm text-primary-foreground/80">
              <li>
                <a href="#" className="hover:text-primary-foreground">
                  Centre d'Aide
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary-foreground">
                  Contact
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary-foreground">
                  Conditions d'Utilisation
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary-foreground">
                  Politique de Confidentialité
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-primary-foreground/20 mt-8 pt-8 text-center">
          <p className="text-sm text-primary-foreground/60">© 2025 AutoValue Maroc. Tous droits réservés.</p>
        </div>
      </div>
    </footer>
  )
}

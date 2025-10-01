"use client"

import { Search, MapPin } from "lucide-react"
import { Input } from "@/components/ui/input"
import Link from "next/link"

export function Header() {
  return (
    <>
      <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-8">
              <Link href="/" className="flex items-center space-x-2">
                <div className="h-8 w-8 bg-primary rounded-md flex items-center justify-center">
                  <span className="text-primary-foreground font-bold text-sm">AV</span>
                </div>
                <span className="font-semibold text-lg">AutoValue</span>
              </Link>
              <nav className="hidden md:flex items-center space-x-6">
                <Link href="/voitures-neuves" className="text-sm font-medium hover:text-primary transition-colors">
                  Voitures Neuves
                </Link>
                <Link href="/" className="text-sm font-medium hover:text-primary transition-colors">
                  Voitures d'Occasion
                </Link>
              </nav>
            </div>

            <div className="flex items-center space-x-4">
              <div className="hidden md:flex items-center space-x-2 bg-muted rounded-lg px-3 py-2">
                <Search className="h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Rechercher..."
                  className="border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 w-48"
                />
              </div>
              <div className="flex items-center space-x-1 text-sm text-muted-foreground">
                <MapPin className="h-4 w-4" />
                <span>Maroc</span>
              </div>
            </div>
          </div>
        </div>
      </header>
    </>
  )
}

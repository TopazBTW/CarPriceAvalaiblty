"use client"

import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { NewCarsHero } from "@/components/new-cars-hero"
import { CarBrandsGrid } from "@/components/car-brands-grid"
import { NewCarBenefits } from "@/components/new-car-benefits"
import { BodyTypeCategories } from "@/components/body-type-categories"
import { CarsByPriceRange } from "@/components/cars-by-price-range"

export default function VoituresNeuvesPage() {
  return (
    <div className="min-h-screen">
      <Header />
      <main>
        <NewCarsHero />
        <CarBrandsGrid />
        <NewCarBenefits />
        <BodyTypeCategories />
        <CarsByPriceRange />
      </main>
      <Footer />
    </div>
  )
}

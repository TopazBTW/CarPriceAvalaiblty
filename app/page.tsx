"use client"

import { Header } from "@/components/header"
import { HeroSection } from "@/components/hero-section"
import { FeaturesSection } from "@/components/features-section"
import { SmartCarPricePrediction } from "@/components/smart-car-prediction"
import { CitiesSection } from "@/components/cities-section"
import { PopularCarsSection } from "@/components/popular-cars-section"
import { FAQSection } from "@/components/faq-section"
import { Footer } from "@/components/footer"

export default function HomePage() {
  return (
    <div className="min-h-screen">
      <Header />
      <main>
        <HeroSection />
        <SmartCarPricePrediction />
        <FeaturesSection />
        <CitiesSection />
        <PopularCarsSection />
        <FAQSection />
      </main>
      <Footer />
    </div>
  )
}

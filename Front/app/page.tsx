"use client"

import { Header } from "@/components/header"
import { HeroSection } from "@/components/hero-section"
import { FeaturesSection } from "@/components/features-section"
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
        <FeaturesSection />
        <CitiesSection />
        <PopularCarsSection />
        <FAQSection />
      </main>
      <Footer />
    </div>
  )
}

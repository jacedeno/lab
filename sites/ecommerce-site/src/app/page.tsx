import HeroBanner from '@/components/home/HeroBanner'
import CategoryGrid from '@/components/home/CategoryGrid'
import FeaturedProducts from '@/components/home/FeaturedProducts'
import ServicesSection from '@/components/home/ServicesSection'
import Newsletter from '@/components/home/Newsletter'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import TrustBar from '@/components/layout/TrustBar'

export default function HomePage() {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <TrustBar />
      <main className="flex-1">
        <HeroBanner />
        <CategoryGrid />
        <FeaturedProducts />
        <ServicesSection />
        <Newsletter />
      </main>
      <Footer />
    </div>
  )
}

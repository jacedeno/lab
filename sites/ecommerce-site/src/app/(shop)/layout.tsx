import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import TrustBar from '@/components/layout/TrustBar'

export default function ShopLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <TrustBar />
      <main className="flex-1">
        {children}
      </main>
      <Footer />
    </div>
  )
}

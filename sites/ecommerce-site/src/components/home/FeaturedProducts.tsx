'use client'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import ProductCard from '@/components/products/ProductCard'
import SectionHeader from '@/components/shared/SectionHeader'
import { getFeaturedProducts, getNewArrivals } from '@/data/mock-products'
import { mockProducts } from '@/data/mock-products'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { ArrowRight } from 'lucide-react'

export default function FeaturedProducts() {
  const featured = getFeaturedProducts().slice(0, 8)
  const newArrivals = getNewArrivals().slice(0, 8)
  const topRated = [...mockProducts].sort((a, b) => (b.rating || 0) - (a.rating || 0)).slice(0, 8)

  return (
    <section className="py-12 bg-[#111827]/30">
      <div className="container mx-auto px-4">
        <div className="flex items-start justify-between mb-8">
          <SectionHeader title="Featured Products" subtitle="Handpicked top performers" className="mb-0" />
          <Button variant="ghost" asChild className="text-[#22d3ee] hover:text-[#22d3ee]/80 hidden sm:flex">
            <Link href="/products">View All <ArrowRight className="ml-1 h-4 w-4" /></Link>
          </Button>
        </div>
        <Tabs defaultValue="featured">
          <TabsList className="bg-[#1f2937] border border-[#374151] mb-6">
            <TabsTrigger value="featured" className="data-[state=active]:bg-[#3b82f6] data-[state=active]:text-white text-gray-400">Featured</TabsTrigger>
            <TabsTrigger value="new" className="data-[state=active]:bg-[#3b82f6] data-[state=active]:text-white text-gray-400">New Arrivals</TabsTrigger>
            <TabsTrigger value="top" className="data-[state=active]:bg-[#3b82f6] data-[state=active]:text-white text-gray-400">Top Rated</TabsTrigger>
          </TabsList>
          <TabsContent value="featured">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {featured.map(p => <ProductCard key={p.id} product={p} />)}
            </div>
          </TabsContent>
          <TabsContent value="new">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {newArrivals.map(p => <ProductCard key={p.id} product={p} />)}
            </div>
          </TabsContent>
          <TabsContent value="top">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {topRated.map(p => <ProductCard key={p.id} product={p} />)}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </section>
  )
}

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ArrowRight, Cpu, Zap } from 'lucide-react'

export default function HeroBanner() {
  return (
    <section className="relative overflow-hidden bg-[#030712]">
      {/* Background glow */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#3b82f6]/10 via-transparent to-[#22d3ee]/5 pointer-events-none" />
      <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-[#3b82f6]/10 rounded-full blur-3xl pointer-events-none" />
      
      <div className="container mx-auto px-4 py-16 lg:py-24">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left: Content */}
          <div className="animate-slide-up">
            <Badge className="mb-4 bg-[#22d3ee]/10 text-[#22d3ee] border-[#22d3ee]/30 hover:bg-[#22d3ee]/20">
              <Zap className="h-3 w-3 mr-1" />
              New Arrivals 2026
            </Badge>
            <h1 className="text-4xl lg:text-6xl font-extrabold text-white leading-tight mb-6">
              Build Your{' '}
              <span className="bg-gradient-to-r from-[#3b82f6] to-[#22d3ee] bg-clip-text text-transparent">
                Ultimate
              </span>{' '}
              Setup
            </h1>
            <p className="text-lg text-gray-400 mb-8 max-w-lg">
              Premium computer hardware, cutting-edge components, and expert IT consulting. 
              Everything you need to dominate — at unbeatable prices.
            </p>
            <div className="flex flex-wrap gap-4">
              <Button size="lg" asChild className="bg-[#3b82f6] hover:bg-[#2563eb] text-white shadow-glow-blue">
                <Link href="/products">
                  Shop All Products <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" asChild className="border-[#374151] text-gray-300 hover:bg-[#1f2937] hover:text-white">
                <Link href="/services">IT Services</Link>
              </Button>
            </div>
            {/* Stats */}
            <div className="flex gap-8 mt-10 pt-8 border-t border-[#374151]">
              {[
                { value: '500+', label: 'Products' },
                { value: '10K+', label: 'Happy Customers' },
                { value: '24/7', label: 'Support' },
              ].map(stat => (
                <div key={stat.label}>
                  <p className="text-2xl font-bold text-[#22d3ee]">{stat.value}</p>
                  <p className="text-sm text-gray-500">{stat.label}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Right: Visual */}
          <div className="relative hidden lg:flex items-center justify-center">
            <div className="relative">
              {/* Main image placeholder */}
              <div className="w-full max-w-md aspect-square rounded-2xl bg-gradient-to-br from-[#1f2937] to-[#111827] border border-[#374151] flex items-center justify-center shadow-card-hover">
                <div className="text-center">
                  <Cpu className="h-24 w-24 text-[#3b82f6] mx-auto mb-4 opacity-60" />
                  <p className="text-gray-500 text-sm">High-performance hardware</p>
                </div>
              </div>
              {/* Floating badges */}
              <div className="absolute -top-4 -right-4 bg-[#1f2937] border border-[#22d3ee]/30 rounded-xl p-3 shadow-card-hover">
                <p className="text-xs text-gray-400">RTX 4090</p>
                <p className="text-sm font-bold text-[#22d3ee]">In Stock</p>
              </div>
              <div className="absolute -bottom-4 -left-4 bg-[#1f2937] border border-[#3b82f6]/30 rounded-xl p-3 shadow-card-hover">
                <p className="text-xs text-gray-400">Free Shipping</p>
                <p className="text-sm font-bold text-[#3b82f6]">Orders $99+</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

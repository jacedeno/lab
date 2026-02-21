import ServiceCard from './ServiceCard'
import SectionHeader from '@/components/shared/SectionHeader'
import { getFeaturedServices } from '@/data/mock-services'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { ArrowRight } from 'lucide-react'

export default function ServicesSection() {
  const services = getFeaturedServices()

  return (
    <section className="py-12">
      <div className="container mx-auto px-4">
        <div className="flex items-start justify-between mb-8">
          <SectionHeader
            title="IT Consulting Services"
            subtitle="Expert solutions for your business technology needs"
            className="mb-0"
          />
          <Button variant="ghost" asChild className="text-[#22d3ee] hover:text-[#22d3ee]/80 hidden sm:flex">
            <Link href="/services">All Services <ArrowRight className="ml-1 h-4 w-4" /></Link>
          </Button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {services.map((service, i) => (
            <ServiceCard key={service.id} service={service} featured={i === 1} />
          ))}
        </div>
      </div>
    </section>
  )
}

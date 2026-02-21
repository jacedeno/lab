import { mockServices } from '@/data/mock-services'
import ServiceCard from '@/components/home/ServiceCard'
import SectionHeader from '@/components/shared/SectionHeader'
import { Button } from '@/components/ui/button'
import { ArrowRight, CheckCircle, Users, Award, Clock } from 'lucide-react'

export default function ServicesPage() {
  return (
    <div>
      {/* Hero */}
      <section className="bg-gradient-to-b from-[#111827] to-[#030712] py-16">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-4xl lg:text-5xl font-extrabold text-white mb-4">
            IT Consulting{' '}
            <span className="bg-gradient-to-r from-[#3b82f6] to-[#22d3ee] bg-clip-text text-transparent">
              Services
            </span>
          </h1>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto mb-8">
            From infrastructure assessment to cloud migration, our certified IT experts deliver enterprise-grade solutions for businesses of all sizes.
          </p>
          <div className="flex flex-wrap justify-center gap-6 text-sm text-gray-400">
            {[
              { icon: Users, text: '500+ Happy Clients' },
              { icon: Award, text: 'ISO 27001 Certified' },
              { icon: Clock, text: '24/7 Support' },
            ].map(({ icon: Icon, text }) => (
              <div key={text} className="flex items-center gap-2">
                <Icon className="h-4 w-4 text-[#22d3ee]" />
                {text}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Services Grid */}
      <section className="container mx-auto px-4 py-12">
        <SectionHeader title="Our Services" subtitle="Choose the right plan for your business" align="center" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {mockServices.map((service, i) => (
            <ServiceCard key={service.id} service={service} featured={i === 1} />
          ))}
        </div>
      </section>

      {/* Process Section */}
      <section className="bg-[#111827]/50 border-y border-[#374151] py-12">
        <div className="container mx-auto px-4">
          <SectionHeader title="How It Works" subtitle="Our proven 4-step process" align="center" />
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { step: '01', title: 'Consultation', desc: 'Free initial consultation to understand your needs and goals.' },
              { step: '02', title: 'Assessment', desc: 'Thorough analysis of your current infrastructure and requirements.' },
              { step: '03', title: 'Implementation', desc: 'Expert deployment following industry best practices.' },
              { step: '04', title: 'Support', desc: 'Ongoing monitoring and support to ensure optimal performance.' },
            ].map(item => (
              <div key={item.step} className="text-center p-6 rounded-xl bg-[#111827] border border-[#374151]">
                <span className="text-4xl font-black text-[#3b82f6]/30">{item.step}</span>
                <h3 className="text-white font-bold mt-2 mb-2">{item.title}</h3>
                <p className="text-sm text-gray-400">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="container mx-auto px-4 py-16 text-center">
        <div className="max-w-2xl mx-auto bg-gradient-to-r from-[#1f2937] to-[#111827] rounded-2xl border border-[#3b82f6]/30 p-8">
          <h2 className="text-2xl font-bold text-white mb-3">Ready to Get Started?</h2>
          <p className="text-gray-400 mb-6">Contact us today for a free consultation. No obligation, no pressure.</p>
          <Button size="lg" className="bg-[#3b82f6] hover:bg-[#2563eb] text-white shadow-glow-blue">
            Schedule Free Consultation <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </section>
    </div>
  )
}

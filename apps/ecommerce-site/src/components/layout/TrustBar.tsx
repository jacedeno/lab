import { Truck, Shield, RefreshCcw, Headphones } from 'lucide-react'

const trustItems = [
  { icon: Truck, title: 'Free Shipping', desc: 'On orders over $99' },
  { icon: Shield, title: 'Secure Payment', desc: '256-bit SSL encryption' },
  { icon: RefreshCcw, title: '30-Day Returns', desc: 'Hassle-free returns' },
  { icon: Headphones, title: '24/7 Support', desc: 'Expert tech support' },
]

export default function TrustBar() {
  return (
    <div className="border-b border-[#374151] bg-[#111827]/50">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 py-4">
          {trustItems.map((item) => (
            <div key={item.title} className="flex items-center gap-3">
              <div className="shrink-0 p-2 rounded-lg bg-[#1f2937] text-[#22d3ee]">
                <item.icon className="h-4 w-4" />
              </div>
              <div>
                <p className="text-sm font-semibold text-white">{item.title}</p>
                <p className="text-xs text-gray-500">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

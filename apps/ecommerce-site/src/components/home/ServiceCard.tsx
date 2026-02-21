import { Service } from '@/types/service'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Check, ArrowRight, Search, Headphones, Server, Cloud, Shield, ShoppingCart } from 'lucide-react'
import Link from 'next/link'
import { formatPrice } from '@/lib/formatters'
import { cn } from '@/lib/utils'

const ICON_MAP: Record<string, React.ElementType> = {
  Search, Headphones, Server, Cloud, Shield, ShoppingCart,
}

const TIER_COLORS: Record<string, string> = {
  BASIC: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  STANDARD: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  PREMIUM: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  ENTERPRISE: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
}

interface ServiceCardProps {
  service: Service
  featured?: boolean
}

export default function ServiceCard({ service, featured = false }: ServiceCardProps) {
  const Icon = ICON_MAP[service.iconName] || Server

  return (
    <div className={cn(
      'relative flex flex-col rounded-xl border p-6 transition-all duration-300 hover:shadow-card-hover',
      featured
        ? 'bg-gradient-to-b from-[#1f2937] to-[#111827] border-[#3b82f6]/40 shadow-glow-blue'
        : 'bg-[#111827] border-[#374151] hover:border-[#3b82f6]/30'
    )}>
      {featured && (
        <div className="absolute -top-3 left-6">
          <Badge className="bg-[#3b82f6] text-white border-0 text-xs">Most Popular</Badge>
        </div>
      )}

      <div className="flex items-start gap-4 mb-4">
        <div className="p-2.5 rounded-xl bg-[#030712] border border-[#374151] text-[#22d3ee]">
          <Icon className="h-5 w-5" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="font-bold text-white">{service.name}</h3>
            <Badge className={cn('text-[10px] border', TIER_COLORS[service.tier])}>{service.tier}</Badge>
          </div>
          <p className="text-sm text-gray-400 mt-1">{service.shortDesc}</p>
        </div>
      </div>

      <div className="mb-4">
        <span className="text-sm text-gray-500">Starting from </span>
        <span className="text-xl font-bold text-white">
          {service.priceFrom === 0 ? 'Free' : formatPrice(service.priceFrom)}
        </span>
        {service.priceFrom > 0 && <span className="text-sm text-gray-500">/project</span>}
      </div>

      <ul className="space-y-2 mb-6 flex-1">
        {service.features.slice(0, 4).map((f) => (
          <li key={f} className="flex items-start gap-2 text-sm text-gray-400">
            <Check className="h-4 w-4 text-[#22d3ee] shrink-0 mt-0.5" />
            {f}
          </li>
        ))}
      </ul>

      <Button asChild className={cn('w-full', featured ? 'bg-[#3b82f6] hover:bg-[#2563eb] text-white' : 'variant-outline border-[#374151] hover:bg-[#1f2937] text-gray-300 bg-transparent hover:text-white')}>
        <Link href={`/services`}>
          Learn More <ArrowRight className="ml-2 h-4 w-4" />
        </Link>
      </Button>
    </div>
  )
}

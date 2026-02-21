import { cn } from '@/lib/utils'

interface SectionHeaderProps {
  title: string
  subtitle?: string
  align?: 'left' | 'center'
  className?: string
}

export default function SectionHeader({ title, subtitle, align = 'left', className }: SectionHeaderProps) {
  return (
    <div className={cn('mb-8', align === 'center' && 'text-center', className)}>
      <h2 className="text-2xl md:text-3xl font-bold text-white">{title}</h2>
      {subtitle && <p className="mt-2 text-gray-400">{subtitle}</p>}
      <div className={cn('mt-3 h-0.5 w-12 bg-gradient-to-r from-[#3b82f6] to-[#22d3ee]', align === 'center' && 'mx-auto')} />
    </div>
  )
}

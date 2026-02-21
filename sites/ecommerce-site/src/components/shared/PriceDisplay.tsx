import { cn } from '@/lib/utils'
import { calculateDiscount } from '@/lib/formatters'

interface PriceDisplayProps {
  price: number
  comparePrice?: number
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export default function PriceDisplay({ price, comparePrice, size = 'md', className }: PriceDisplayProps) {
  const discount = comparePrice ? calculateDiscount(price, comparePrice) : 0
  const format = (n: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0 }).format(n)

  const sizeClasses = {
    sm: { price: 'text-base font-semibold', compare: 'text-xs', badge: 'text-[10px] px-1' },
    md: { price: 'text-xl font-bold', compare: 'text-sm', badge: 'text-xs px-1.5' },
    lg: { price: 'text-3xl font-bold', compare: 'text-base', badge: 'text-sm px-2' },
  }

  const s = sizeClasses[size]

  return (
    <div className={cn('flex items-center gap-2 flex-wrap', className)}>
      <span className={cn(s.price, 'text-white')}>{format(price)}</span>
      {comparePrice && comparePrice > price && (
        <>
          <span className={cn(s.compare, 'text-gray-500 line-through')}>{format(comparePrice)}</span>
          <span className={cn(s.badge, 'py-0.5 rounded font-semibold bg-green-500/20 text-green-400')}>
            -{discount}%
          </span>
        </>
      )}
    </div>
  )
}

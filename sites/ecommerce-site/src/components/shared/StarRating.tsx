import { Star } from 'lucide-react'
import { cn } from '@/lib/utils'

interface StarRatingProps {
  rating: number
  reviewCount?: number
  size?: 'sm' | 'md'
  className?: string
}

export default function StarRating({ rating, reviewCount, size = 'sm', className }: StarRatingProps) {
  const stars = Array.from({ length: 5 }, (_, i) => {
    const filled = i + 1 <= Math.floor(rating)
    const half = !filled && i < rating
    return { filled, half }
  })

  const iconSize = size === 'sm' ? 'h-3 w-3' : 'h-4 w-4'

  return (
    <div className={cn('flex items-center gap-1', className)}>
      <div className="flex">
        {stars.map((star, i) => (
          <Star
            key={i}
            className={cn(
              iconSize,
              star.filled ? 'text-[#f59e0b] fill-[#f59e0b]' :
              star.half ? 'text-[#f59e0b] fill-[#f59e0b]/50' :
              'text-gray-600 fill-gray-600/20'
            )}
          />
        ))}
      </div>
      {reviewCount !== undefined && (
        <span className="text-xs text-gray-500">({reviewCount.toLocaleString()})</span>
      )}
    </div>
  )
}

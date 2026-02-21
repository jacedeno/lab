'use client'
import { Heart } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { Product } from '@/types/product'
import { useWishlist } from '@/hooks/useWishlist'

interface WishlistButtonProps {
  product: Product
  className?: string
  size?: 'sm' | 'md'
}

export default function WishlistButton({ product, className, size = 'sm' }: WishlistButtonProps) {
  const { toggle, isInWishlist } = useWishlist()
  const inWishlist = isInWishlist(product.id)

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={(e) => { e.preventDefault(); e.stopPropagation(); toggle(product) }}
      className={cn(
        'rounded-full transition-all',
        size === 'sm' ? 'h-7 w-7' : 'h-9 w-9',
        inWishlist
          ? 'text-red-400 hover:text-red-300 bg-red-500/10 hover:bg-red-500/20'
          : 'text-gray-400 hover:text-red-400 bg-black/40 hover:bg-black/60',
        className
      )}
    >
      <Heart className={cn(size === 'sm' ? 'h-3.5 w-3.5' : 'h-4 w-4', inWishlist && 'fill-current')} />
    </Button>
  )
}

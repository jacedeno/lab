'use client'
import { useState } from 'react'
import { ShoppingCart, Check } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Product } from '@/types/product'
import { useCart } from '@/hooks/useCart'
import { cn } from '@/lib/utils'

interface AddToCartButtonProps {
  product: Product
  quantity: number
  className?: string
}

export default function AddToCartButton({ product, quantity, className }: AddToCartButtonProps) {
  const { addItem } = useCart()
  const [added, setAdded] = useState(false)

  const handleAdd = () => {
    addItem(product, quantity)
    setAdded(true)
    setTimeout(() => setAdded(false), 2000)
  }

  if (product.stock === 0) {
    return (
      <Button disabled size="lg" className={cn('w-full', className)}>
        Out of Stock
      </Button>
    )
  }

  return (
    <Button
      size="lg"
      onClick={handleAdd}
      className={cn(
        'w-full transition-all',
        added
          ? 'bg-green-600 hover:bg-green-700 text-white'
          : 'bg-[#3b82f6] hover:bg-[#2563eb] text-white shadow-glow-blue',
        className
      )}
    >
      {added ? (
        <>
          <Check className="h-5 w-5 mr-2" />
          Added to Cart!
        </>
      ) : (
        <>
          <ShoppingCart className="h-5 w-5 mr-2" />
          Add to Cart
        </>
      )}
    </Button>
  )
}

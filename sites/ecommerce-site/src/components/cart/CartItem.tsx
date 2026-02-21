'use client'
import Image from 'next/image'
import Link from 'next/link'
import { Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { CartItem as CartItemType } from '@/types/cart'
import { useCart } from '@/hooks/useCart'
import { formatPrice } from '@/lib/formatters'
import QuantitySelector from '@/components/product-detail/QuantitySelector'

interface CartItemProps {
  item: CartItemType
}

export default function CartItem({ item }: CartItemProps) {
  const { updateQuantity, removeItem } = useCart()
  const { product, quantity } = item

  return (
    <div className="flex gap-4 bg-[#111827] border border-[#374151] rounded-xl p-4">
      {/* Image */}
      <Link href={`/products/${product.categorySlug}/${product.slug}`} className="shrink-0">
        <div className="relative w-20 h-20 sm:w-24 sm:h-24 rounded-lg overflow-hidden bg-[#1f2937]">
          <Image src={product.thumbnailUrl} alt={product.name} fill className="object-cover" sizes="96px" />
        </div>
      </Link>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <p className="text-xs text-gray-500 mb-0.5">{product.brand}</p>
        <Link href={`/products/${product.categorySlug}/${product.slug}`} className="block">
          <h3 className="text-sm font-semibold text-white hover:text-[#22d3ee] transition-colors line-clamp-2">{product.name}</h3>
        </Link>
        <p className="text-xs text-gray-500 mt-1">SKU: {product.sku}</p>

        <div className="flex items-center justify-between mt-3 flex-wrap gap-2">
          <QuantitySelector
            value={quantity}
            onChange={(q) => updateQuantity(product.id, q)}
            max={product.stock}
          />
          <div className="flex items-center gap-3">
            <span className="font-bold text-white">{formatPrice(product.price * quantity)}</span>
            {quantity > 1 && (
              <span className="text-xs text-gray-500">{formatPrice(product.price)} each</span>
            )}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => removeItem(product.id)}
              className="h-8 w-8 text-gray-500 hover:text-red-400 hover:bg-red-500/10"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

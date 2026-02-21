'use client'
import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { Truck, Shield, RefreshCcw, Share2 } from 'lucide-react'
import { Product } from '@/types/product'
import PriceDisplay from '@/components/shared/PriceDisplay'
import StarRating from '@/components/shared/StarRating'
import WishlistButton from '@/components/shared/WishlistButton'
import QuantitySelector from './QuantitySelector'
import AddToCartButton from './AddToCartButton'
import { siteConfig } from '@/config/site'

interface ProductInfoProps {
  product: Product
}

export default function ProductInfo({ product }: ProductInfoProps) {
  const [quantity, setQuantity] = useState(1)

  return (
    <div className="space-y-6">
      {/* Badges */}
      <div className="flex flex-wrap gap-2">
        {product.isNewArrival && (
          <Badge className="bg-[#8b5cf6] text-white border-0">New Arrival</Badge>
        )}
        {product.stock > 0 ? (
          <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
            In Stock ({product.stock} available)
          </Badge>
        ) : (
          <Badge className="bg-red-500/20 text-red-400 border-red-500/30">Out of Stock</Badge>
        )}
        <Badge className="bg-[#1f2937] text-gray-400 border-[#374151]">SKU: {product.sku}</Badge>
      </div>

      {/* Brand */}
      <p className="text-sm text-[#22d3ee] font-medium">{product.brand}</p>

      {/* Name */}
      <h1 className="text-2xl lg:text-3xl font-bold text-white leading-tight">{product.name}</h1>

      {/* Rating */}
      {product.rating && (
        <div className="flex items-center gap-3">
          <StarRating rating={product.rating} reviewCount={product.reviewCount} size="md" />
          <Separator orientation="vertical" className="h-4 bg-[#374151]" />
          <a href="#reviews" className="text-sm text-[#3b82f6] hover:text-[#60a5fa]">Write a review</a>
        </div>
      )}

      {/* Price */}
      <PriceDisplay price={product.price} comparePrice={product.comparePrice} size="lg" />

      <Separator className="bg-[#374151]" />

      {/* Description */}
      <p className="text-gray-400 leading-relaxed">{product.description}</p>

      {/* Tags */}
      <div className="flex flex-wrap gap-2">
        {product.tags.map(tag => (
          <span key={tag} className="text-xs text-gray-500 bg-[#1f2937] border border-[#374151] rounded px-2 py-1">
            #{tag}
          </span>
        ))}
      </div>

      <Separator className="bg-[#374151]" />

      {/* Quantity + Add to Cart */}
      <div className="space-y-3">
        <div className="flex items-center gap-4">
          <label className="text-sm text-gray-400">Quantity:</label>
          <QuantitySelector value={quantity} onChange={setQuantity} max={product.stock} />
        </div>
        <div className="flex gap-3">
          <AddToCartButton product={product} quantity={quantity} className="flex-1" />
          <WishlistButton product={product} size="md" className="h-11 w-11 border border-[#374151] rounded-lg" />
          <Button variant="outline" size="icon" className="h-11 w-11 border-[#374151] text-gray-400 hover:text-white hover:bg-[#1f2937]">
            <Share2 className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Trust badges */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { icon: Truck, text: `Free shipping over $${siteConfig.shipping.freeThreshold}` },
          { icon: Shield, text: '2-year warranty' },
          { icon: RefreshCcw, text: '30-day returns' },
        ].map(({ icon: Icon, text }) => (
          <div key={text} className="flex flex-col items-center text-center gap-1 p-2 rounded-lg bg-[#1f2937] border border-[#374151]">
            <Icon className="h-4 w-4 text-[#22d3ee]" />
            <span className="text-[11px] text-gray-400">{text}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

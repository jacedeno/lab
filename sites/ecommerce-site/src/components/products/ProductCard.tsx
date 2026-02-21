'use client'
import Link from 'next/link'
import Image from 'next/image'
import { ShoppingCart } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Product } from '@/types/product'
import { useCart } from '@/hooks/useCart'
import PriceDisplay from '@/components/shared/PriceDisplay'
import StarRating from '@/components/shared/StarRating'
import WishlistButton from '@/components/shared/WishlistButton'
import { cn } from '@/lib/utils'

interface ProductCardProps {
  product: Product
  viewMode?: 'grid' | 'list'
}

export default function ProductCard({ product, viewMode = 'grid' }: ProductCardProps) {
  const { addItem } = useCart()

  const handleAddToCart = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    addItem(product, 1)
  }

  if (viewMode === 'list') {
    return (
      <Link href={`/products/${product.categorySlug}/${product.slug}`} className="block">
        <div className="group flex gap-4 bg-[#111827] border border-[#374151] rounded-xl p-4 hover:border-[#3b82f6]/50 hover:shadow-card-hover transition-all duration-300">
          <div className="relative shrink-0 w-32 h-24 rounded-lg overflow-hidden bg-[#1f2937]">
            <Image src={product.thumbnailUrl} alt={product.name} fill className="object-cover group-hover:scale-105 transition-transform duration-300" sizes="128px" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs text-gray-500 mb-1">{product.brand}</p>
            <h3 className="font-semibold text-white group-hover:text-[#22d3ee] transition-colors line-clamp-2">{product.name}</h3>
            {product.rating && <StarRating rating={product.rating} reviewCount={product.reviewCount} className="mt-1" />}
            <PriceDisplay price={product.price} comparePrice={product.comparePrice} size="sm" className="mt-2" />
          </div>
          <div className="flex flex-col items-end justify-between shrink-0">
            <WishlistButton product={product} />
            <Button size="sm" onClick={handleAddToCart} className="bg-[#3b82f6] hover:bg-[#2563eb] text-white">
              <ShoppingCart className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </Link>
    )
  }

  return (
    <Link href={`/products/${product.categorySlug}/${product.slug}`} className="block group">
      <div className="relative bg-[#111827] border border-[#374151] rounded-xl overflow-hidden hover:border-[#3b82f6]/50 hover:shadow-card-hover transition-all duration-300">
        {/* Badges */}
        <div className="absolute top-2 left-2 z-10 flex flex-col gap-1">
          {product.isNewArrival && (
            <Badge className="bg-[#8b5cf6] text-white border-0 text-[10px] px-1.5 py-0.5">NEW</Badge>
          )}
          {product.comparePrice && product.comparePrice > product.price && (
            <Badge className="bg-green-500/20 text-green-400 border-green-500/30 text-[10px] px-1.5 py-0.5">
              SALE
            </Badge>
          )}
          {product.stock < 5 && product.stock > 0 && (
            <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30 text-[10px] px-1.5 py-0.5">
              LOW STOCK
            </Badge>
          )}
        </div>

        {/* Wishlist */}
        <div className="absolute top-2 right-2 z-10">
          <WishlistButton product={product} />
        </div>

        {/* Image */}
        <div className="relative aspect-[4/3] overflow-hidden bg-[#1f2937]">
          <Image
            src={product.thumbnailUrl}
            alt={product.name}
            fill
            className="object-cover group-hover:scale-105 transition-transform duration-500"
            sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 25vw"
          />
        </div>

        {/* Content */}
        <div className="p-3">
          <p className="text-xs text-gray-500 mb-1">{product.brand}</p>
          <h3 className="text-sm font-semibold text-white line-clamp-2 group-hover:text-[#22d3ee] transition-colors mb-2 min-h-[2.5rem]">
            {product.name}
          </h3>

          {/* Key specs chips */}
          <div className="flex flex-wrap gap-1 mb-2">
            {product.specs.slice(0, 2).map(spec => (
              spec.value.length < 20 && (
                <span key={spec.id} className="text-[10px] text-[#22d3ee] bg-[#22d3ee]/10 border border-[#22d3ee]/20 rounded px-1.5 py-0.5">
                  {spec.value}
                </span>
              )
            ))}
          </div>

          {/* Rating */}
          {product.rating && (
            <StarRating rating={product.rating} reviewCount={product.reviewCount} className="mb-2" />
          )}

          {/* Price */}
          <PriceDisplay price={product.price} comparePrice={product.comparePrice} size="sm" className="mb-3" />

          {/* Add to Cart */}
          <Button
            size="sm"
            onClick={handleAddToCart}
            disabled={product.stock === 0}
            className="w-full bg-[#3b82f6] hover:bg-[#2563eb] text-white disabled:opacity-50"
          >
            <ShoppingCart className="h-4 w-4 mr-2" />
            {product.stock === 0 ? 'Out of Stock' : 'Add to Cart'}
          </Button>
        </div>
      </div>
    </Link>
  )
}

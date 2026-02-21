import ProductCard from './ProductCard'
import { Product } from '@/types/product'
import { ProductGridSkeleton } from '@/components/shared/LoadingSkeleton'
import EmptyState from '@/components/shared/EmptyState'
import { Package } from 'lucide-react'

interface ProductGridProps {
  products: Product[]
  viewMode?: 'grid' | 'list'
  isLoading?: boolean
}

export default function ProductGrid({ products, viewMode = 'grid', isLoading = false }: ProductGridProps) {
  if (isLoading) return <ProductGridSkeleton />

  if (products.length === 0) {
    return (
      <EmptyState
        icon={Package}
        title="No products found"
        description="Try adjusting your filters or search terms to find what you are looking for."
        actionLabel="Clear Filters"
        actionHref="/products"
      />
    )
  }

  if (viewMode === 'list') {
    return (
      <div className="flex flex-col gap-3">
        {products.map(product => (
          <ProductCard key={product.id} product={product} viewMode="list" />
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {products.map(product => (
        <ProductCard key={product.id} product={product} viewMode="grid" />
      ))}
    </div>
  )
}

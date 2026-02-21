import ProductCard from '@/components/products/ProductCard'
import SectionHeader from '@/components/shared/SectionHeader'
import { Product } from '@/types/product'
import { getRelatedProducts } from '@/data/mock-products'

interface RelatedProductsProps {
  product: Product
}

export default function RelatedProducts({ product }: RelatedProductsProps) {
  const related = getRelatedProducts(product, 4)

  if (related.length === 0) return null

  return (
    <section className="mt-12">
      <SectionHeader title="Related Products" subtitle="You might also like these" />
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {related.map(p => (
          <ProductCard key={p.id} product={p} />
        ))}
      </div>
    </section>
  )
}

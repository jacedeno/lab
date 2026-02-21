import { notFound } from 'next/navigation'
import { getProductBySlug } from '@/data/mock-products'
import ImageGallery from '@/components/product-detail/ImageGallery'
import ProductInfo from '@/components/product-detail/ProductInfo'
import SpecsTable from '@/components/product-detail/SpecsTable'
import ReviewSection from '@/components/product-detail/ReviewSection'
import RelatedProducts from '@/components/product-detail/RelatedProducts'
import Breadcrumb from '@/components/shared/Breadcrumb'
import { mockCategories } from '@/data/mock-categories'

export default async function ProductDetailPage({ params }: { params: Promise<{ category: string; slug: string }> }) {
  const { category: categorySlug, slug } = await params
  const product = getProductBySlug(slug)
  if (!product) notFound()

  const category = mockCategories.find(c => c.slug === categorySlug)

  return (
    <div className="container mx-auto px-4 py-8">
      <Breadcrumb
        items={[
          { label: 'Products', href: '/products' },
          { label: category?.name || categorySlug, href: `/products/${categorySlug}` },
          { label: product.name },
        ]}
        className="mb-6"
      />

      {/* Main product section */}
      <div className="grid lg:grid-cols-2 gap-8 mb-12">
        <ImageGallery images={product.imageUrls} productName={product.name} />
        <ProductInfo product={product} />
      </div>

      {/* Specs + Reviews */}
      <div className="grid lg:grid-cols-3 gap-6 mb-12">
        <div className="lg:col-span-2">
          <SpecsTable product={product} />
        </div>
        <div>
          <ReviewSection productId={product.id} rating={product.rating} reviewCount={product.reviewCount} />
        </div>
      </div>

      {/* Related Products */}
      <RelatedProducts product={product} />
    </div>
  )
}

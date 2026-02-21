export type ProductType = 'PHYSICAL' | 'SERVICE'

export interface ProductSpec {
  id: string
  key: string
  value: string
  unit?: string
  sortOrder: number
}

export interface Product {
  id: string
  categoryId: string
  categorySlug: string
  name: string
  slug: string
  brand: string
  description: string
  price: number
  comparePrice?: number
  sku: string
  stock: number
  isActive: boolean
  isFeatured: boolean
  isNewArrival: boolean
  productType: ProductType
  imageUrls: string[]
  thumbnailUrl: string
  tags: string[]
  specs: ProductSpec[]
  rating?: number
  reviewCount?: number
}

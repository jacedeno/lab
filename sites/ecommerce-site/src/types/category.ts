export interface Category {
  id: string
  name: string
  slug: string
  description: string
  imageUrl: string
  iconName: string
  sortOrder: number
  isActive: boolean
  productCount?: number
}

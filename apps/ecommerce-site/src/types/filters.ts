export interface FilterState {
  brands: string[]
  priceMin: number
  priceMax: number
  inStockOnly: boolean
  newArrivalsOnly: boolean
  specs: Record<string, string[]>
  sortBy: SortOption
  viewMode: 'grid' | 'list'
  page: number
}

export type SortOption = 'featured' | 'price-asc' | 'price-desc' | 'newest' | 'rating' | 'name-asc'

export interface FilterSpec {
  key: string
  label: string
  options: string[]
}

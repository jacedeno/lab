export type ServiceTier = 'BASIC' | 'STANDARD' | 'PREMIUM' | 'ENTERPRISE'

export interface Service {
  id: string
  name: string
  slug: string
  shortDesc: string
  description: string
  tier: ServiceTier
  priceFrom: number
  iconName: string
  features: string[]
  isActive: boolean
  isFeatured: boolean
  sortOrder: number
}

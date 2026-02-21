export type Role = 'CUSTOMER' | 'ADMIN'

export interface Address {
  id: string
  userId: string
  label: string
  line1: string
  line2?: string
  city: string
  state: string
  postalCode: string
  country: string
  isDefault: boolean
}

export interface User {
  id: string
  email: string
  name: string
  role: Role
  avatarUrl?: string
  phone?: string
  addresses: Address[]
  createdAt: string
}

import { Address } from './user'
import { Product } from './product'

export type OrderStatus = 'PENDING' | 'PROCESSING' | 'SHIPPED' | 'DELIVERED' | 'CANCELLED' | 'REFUNDED'

export interface OrderItem {
  id: string
  productId: string
  product: Product
  quantity: number
  unitPrice: number
  totalPrice: number
  productName: string
}

export interface Order {
  id: string
  userId: string
  shippingAddress: Address
  status: OrderStatus
  subtotal: number
  shippingCost: number
  tax: number
  total: number
  notes?: string
  items: OrderItem[]
  createdAt: string
  updatedAt: string
}

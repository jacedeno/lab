'use client'
import { useLocalStorage } from './useLocalStorage'
import { Product } from '@/types/product'

export function useWishlist() {
  const [items, setItems] = useLocalStorage<Product[]>('gz-wishlist', [])

  const toggle = (product: Product) => {
    setItems(prev => {
      const exists = prev.find(p => p.id === product.id)
      if (exists) return prev.filter(p => p.id !== product.id)
      return [...prev, product]
    })
  }

  const isInWishlist = (productId: string) => items.some(p => p.id === productId)
  const count = items.length

  return { items, toggle, isInWishlist, count }
}

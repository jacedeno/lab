'use client'
import { useState, useEffect, useCallback } from 'react'
import { Product } from '@/types/product'
import { mockProducts } from '@/data/mock-products'

export function useSearch() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<Product[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const search = useCallback((q: string) => {
    setQuery(q)
    if (!q.trim()) {
      setResults([])
      return
    }
    setIsLoading(true)
    // Simulate async search
    setTimeout(() => {
      const lower = q.toLowerCase()
      const found = mockProducts.filter(p =>
        p.name.toLowerCase().includes(lower) ||
        p.brand.toLowerCase().includes(lower) ||
        p.description.toLowerCase().includes(lower) ||
        p.tags.some(tag => tag.toLowerCase().includes(lower))
      )
      setResults(found)
      setIsLoading(false)
    }, 200)
  }, [])

  useEffect(() => {
    search(query)
  }, [query, search])

  return { query, setQuery: search, results, isLoading }
}

'use client'
import { useState, useCallback } from 'react'
import { FilterState, SortOption } from '@/types/filters'

const defaultFilters: FilterState = {
  brands: [],
  priceMin: 0,
  priceMax: 10000,
  inStockOnly: false,
  newArrivalsOnly: false,
  specs: {},
  sortBy: 'featured',
  viewMode: 'grid',
  page: 1,
}

export function useFilters(initial?: Partial<FilterState>) {
  const [filters, setFilters] = useState<FilterState>({ ...defaultFilters, ...initial })

  const setFilter = useCallback(<K extends keyof FilterState>(key: K, value: FilterState[K]) => {
    setFilters(prev => ({ ...prev, [key]: value, page: key !== 'page' ? 1 : prev.page }))
  }, [])

  const toggleBrand = useCallback((brand: string) => {
    setFilters(prev => ({
      ...prev,
      brands: prev.brands.includes(brand)
        ? prev.brands.filter(b => b !== brand)
        : [...prev.brands, brand],
      page: 1,
    }))
  }, [])

  const toggleSpec = useCallback((key: string, value: string) => {
    setFilters(prev => {
      const current = prev.specs[key] || []
      return {
        ...prev,
        specs: {
          ...prev.specs,
          [key]: current.includes(value)
            ? current.filter(v => v !== value)
            : [...current, value],
        },
        page: 1,
      }
    })
  }, [])

  const setPriceRange = useCallback((min: number, max: number) => {
    setFilters(prev => ({ ...prev, priceMin: min, priceMax: max, page: 1 }))
  }, [])

  const clearFilters = useCallback(() => {
    setFilters(defaultFilters)
  }, [])

  const activeFilterCount = [
    filters.brands.length > 0,
    filters.inStockOnly,
    filters.newArrivalsOnly,
    filters.priceMin > 0 || filters.priceMax < 10000,
    Object.values(filters.specs).some(arr => arr.length > 0),
  ].filter(Boolean).length

  return { filters, setFilter, toggleBrand, toggleSpec, setPriceRange, clearFilters, activeFilterCount }
}

'use client'
import { useMemo } from 'react'
import { mockProducts } from '@/data/mock-products'
import { mockCategories } from '@/data/mock-categories'
import ProductGrid from '@/components/products/ProductGrid'
import FilterSidebar from '@/components/products/FilterSidebar'
import SortControls from '@/components/products/SortControls'
import ViewToggle from '@/components/products/ViewToggle'
import ActiveFilters from '@/components/products/ActiveFilters'
import MobileFilterDrawer from '@/components/products/MobileFilterDrawer'
import Breadcrumb from '@/components/shared/Breadcrumb'
import SectionHeader from '@/components/shared/SectionHeader'
import { useFilters } from '@/hooks/useFilters'

export default function ProductsPage() {
  const { filters, setFilter, toggleBrand, toggleSpec, setPriceRange, clearFilters, activeFilterCount } = useFilters()

  const availableBrands = useMemo(() =>
    [...new Set(mockProducts.map(p => p.brand))].sort(), [])

  const filtered = useMemo(() => {
    let result = mockProducts.filter(p => p.isActive)
    if (filters.brands.length > 0) result = result.filter(p => filters.brands.includes(p.brand))
    if (filters.inStockOnly) result = result.filter(p => p.stock > 0)
    if (filters.newArrivalsOnly) result = result.filter(p => p.isNewArrival)
    result = result.filter(p => p.price >= filters.priceMin && p.price <= filters.priceMax)
    Object.entries(filters.specs).forEach(([key, values]) => {
      if (values.length > 0) {
        result = result.filter(p => p.specs.some(s => s.key === key && values.includes(s.value)))
      }
    })
    switch (filters.sortBy) {
      case 'price-asc': result.sort((a, b) => a.price - b.price); break
      case 'price-desc': result.sort((a, b) => b.price - a.price); break
      case 'newest': result = result.filter(p => p.isNewArrival).concat(result.filter(p => !p.isNewArrival)); break
      case 'rating': result.sort((a, b) => (b.rating || 0) - (a.rating || 0)); break
      case 'name-asc': result.sort((a, b) => a.name.localeCompare(b.name)); break
      default: result = result.filter(p => p.isFeatured).concat(result.filter(p => !p.isFeatured)); break
    }
    return result
  }, [filters])

  const onFilterChange = { toggleBrand, toggleSpec, setPriceRange, setFilter }

  return (
    <div className="container mx-auto px-4 py-8">
      <Breadcrumb items={[{ label: 'Products' }]} className="mb-6" />
      <SectionHeader title="All Products" subtitle={`${filtered.length} products available`} className="mb-6" />

      <div className="flex gap-8">
        {/* Sidebar - desktop */}
        <div className="hidden lg:block">
          <FilterSidebar filters={filters} onFilterChange={onFilterChange} availableBrands={availableBrands} />
        </div>

        {/* Main content */}
        <div className="flex-1 min-w-0">
          {/* Controls bar */}
          <div className="flex items-center justify-between gap-3 mb-4 flex-wrap">
            <div className="flex items-center gap-2">
              <MobileFilterDrawer filters={filters} onFilterChange={onFilterChange} availableBrands={availableBrands} activeFilterCount={activeFilterCount} />
              <ActiveFilters filters={filters} onRemoveBrand={toggleBrand} onRemoveSpec={toggleSpec} onClearAll={clearFilters} />
            </div>
            <div className="flex items-center gap-2">
              <SortControls value={filters.sortBy} onChange={(v) => setFilter('sortBy', v)} count={filtered.length} />
              <ViewToggle value={filters.viewMode} onChange={(v) => setFilter('viewMode', v)} />
            </div>
          </div>
          <ProductGrid products={filtered} viewMode={filters.viewMode} />
        </div>
      </div>
    </div>
  )
}

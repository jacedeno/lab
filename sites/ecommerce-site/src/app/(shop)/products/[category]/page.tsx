'use client'
import { useMemo } from 'react'
import { notFound } from 'next/navigation'
import { use } from 'react'
import { getProductsByCategory } from '@/data/mock-products'
import { mockCategories } from '@/data/mock-categories'
import { CATEGORY_FILTER_SPECS } from '@/lib/constants'
import ProductGrid from '@/components/products/ProductGrid'
import FilterSidebar from '@/components/products/FilterSidebar'
import SortControls from '@/components/products/SortControls'
import ViewToggle from '@/components/products/ViewToggle'
import ActiveFilters from '@/components/products/ActiveFilters'
import MobileFilterDrawer from '@/components/products/MobileFilterDrawer'
import Breadcrumb from '@/components/shared/Breadcrumb'
import SectionHeader from '@/components/shared/SectionHeader'
import { useFilters } from '@/hooks/useFilters'

export default function CategoryPage({ params }: { params: Promise<{ category: string }> }) {
  const { category: categorySlug } = use(params)
  const category = mockCategories.find(c => c.slug === categorySlug)
  if (!category) notFound()

  const { filters, setFilter, toggleBrand, toggleSpec, setPriceRange, clearFilters, activeFilterCount } = useFilters()
  const allProducts = getProductsByCategory(categorySlug)
  const availableBrands = useMemo(() => [...new Set(allProducts.map(p => p.brand))].sort(), [allProducts])
  const categorySpecs = CATEGORY_FILTER_SPECS[categorySlug] || []

  const filtered = useMemo(() => {
    let result = allProducts.filter(p => p.isActive)
    if (filters.brands.length > 0) result = result.filter(p => filters.brands.includes(p.brand))
    if (filters.inStockOnly) result = result.filter(p => p.stock > 0)
    if (filters.newArrivalsOnly) result = result.filter(p => p.isNewArrival)
    result = result.filter(p => p.price >= filters.priceMin && p.price <= filters.priceMax)
    Object.entries(filters.specs).forEach(([key, values]) => {
      if (values.length > 0) result = result.filter(p => p.specs.some(s => s.key === key && values.includes(s.value)))
    })
    switch (filters.sortBy) {
      case 'price-asc': result.sort((a, b) => a.price - b.price); break
      case 'price-desc': result.sort((a, b) => b.price - a.price); break
      case 'rating': result.sort((a, b) => (b.rating || 0) - (a.rating || 0)); break
      case 'name-asc': result.sort((a, b) => a.name.localeCompare(b.name)); break
      default: result = result.filter(p => p.isFeatured).concat(result.filter(p => !p.isFeatured)); break
    }
    return result
  }, [allProducts, filters])

  const onFilterChange = { toggleBrand, toggleSpec, setPriceRange, setFilter }

  return (
    <div className="container mx-auto px-4 py-8">
      <Breadcrumb items={[{ label: 'Products', href: '/products' }, { label: category.name }]} className="mb-6" />
      <SectionHeader title={category.name} subtitle={category.description} className="mb-6" />

      <div className="flex gap-8">
        <div className="hidden lg:block">
          <FilterSidebar filters={filters} onFilterChange={onFilterChange} availableBrands={availableBrands} categorySpecs={categorySpecs} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-3 mb-4 flex-wrap">
            <div className="flex items-center gap-2">
              <MobileFilterDrawer filters={filters} onFilterChange={onFilterChange} availableBrands={availableBrands} categorySpecs={categorySpecs} activeFilterCount={activeFilterCount} />
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

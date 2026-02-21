'use client'
import { useMemo } from 'react'
import { useSearchParams } from 'next/navigation'
import { Suspense } from 'react'
import { mockProducts } from '@/data/mock-products'
import ProductGrid from '@/components/products/ProductGrid'
import SortControls from '@/components/products/SortControls'
import ViewToggle from '@/components/products/ViewToggle'
import SearchBar from '@/components/shared/SearchBar'
import SectionHeader from '@/components/shared/SectionHeader'
import { useFilters } from '@/hooks/useFilters'
import { Search } from 'lucide-react'

function SearchResults() {
  const searchParams = useSearchParams()
  const query = searchParams.get('q') || ''
  const { filters, setFilter } = useFilters()

  const results = useMemo(() => {
    if (!query.trim()) return []
    const lower = query.toLowerCase()
    return mockProducts.filter(p =>
      p.isActive && (
        p.name.toLowerCase().includes(lower) ||
        p.brand.toLowerCase().includes(lower) ||
        p.description.toLowerCase().includes(lower) ||
        p.tags.some(t => t.toLowerCase().includes(lower))
      )
    )
  }, [query])

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <SearchBar defaultValue={query} className="max-w-xl mb-4" />
        {query ? (
          <SectionHeader
            title={results.length > 0 ? `Results for "${query}"` : `No results for "${query}"`}
            subtitle={results.length > 0 ? `${results.length} products found` : 'Try different keywords or browse our categories'}
          />
        ) : (
          <div className="text-center py-16">
            <Search className="h-12 w-12 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400">Enter a search term to find products</p>
          </div>
        )}
      </div>

      {results.length > 0 && (
        <>
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm text-gray-400">{results.length} results</span>
            <div className="flex items-center gap-2">
              <SortControls value={filters.sortBy} onChange={(v) => setFilter('sortBy', v)} count={results.length} />
              <ViewToggle value={filters.viewMode} onChange={(v) => setFilter('viewMode', v)} />
            </div>
          </div>
          <ProductGrid products={results} viewMode={filters.viewMode} />
        </>
      )}
    </div>
  )
}

export default function SearchPage() {
  return (
    <Suspense fallback={<div className="container mx-auto px-4 py-8 text-gray-400">Searching...</div>}>
      <SearchResults />
    </Suspense>
  )
}

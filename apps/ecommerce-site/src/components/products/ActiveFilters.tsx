'use client'
import { X } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { FilterState } from '@/types/filters'

interface ActiveFiltersProps {
  filters: FilterState
  onRemoveBrand: (brand: string) => void
  onRemoveSpec: (key: string, value: string) => void
  onClearAll: () => void
}

export default function ActiveFilters({ filters, onRemoveBrand, onRemoveSpec, onClearAll }: ActiveFiltersProps) {
  const hasFilters = filters.brands.length > 0 ||
    Object.values(filters.specs).some(arr => arr.length > 0) ||
    filters.inStockOnly || filters.newArrivalsOnly

  if (!hasFilters) return null

  return (
    <div className="flex flex-wrap items-center gap-2 py-2">
      <span className="text-xs text-gray-500">Active filters:</span>
      {filters.brands.map(brand => (
        <Badge key={brand} className="bg-[#1f2937] text-gray-300 border-[#374151] hover:bg-[#374151] cursor-pointer gap-1">
          {brand}
          <button onClick={() => onRemoveBrand(brand)} className="hover:text-white">
            <X className="h-3 w-3" />
          </button>
        </Badge>
      ))}
      {Object.entries(filters.specs).map(([key, values]) =>
        values.map(value => (
          <Badge key={`${key}-${value}`} className="bg-[#1f2937] text-gray-300 border-[#374151] hover:bg-[#374151] cursor-pointer gap-1">
            {value}
            <button onClick={() => onRemoveSpec(key, value)} className="hover:text-white">
              <X className="h-3 w-3" />
            </button>
          </Badge>
        ))
      )}
      {filters.inStockOnly && (
        <Badge className="bg-[#1f2937] text-gray-300 border-[#374151]">In Stock</Badge>
      )}
      <Button variant="ghost" size="sm" onClick={onClearAll} className="text-xs text-[#22d3ee] hover:text-[#22d3ee]/80 h-auto py-1 px-2">
        Clear all
      </Button>
    </div>
  )
}

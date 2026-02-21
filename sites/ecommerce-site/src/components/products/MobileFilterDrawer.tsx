'use client'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { SlidersHorizontal } from 'lucide-react'
import FilterSidebar from './FilterSidebar'
import { FilterState, FilterSpec } from '@/types/filters'

interface MobileFilterDrawerProps {
  filters: FilterState
  onFilterChange: {
    toggleBrand: (brand: string) => void
    toggleSpec: (key: string, value: string) => void
    setPriceRange: (min: number, max: number) => void
    setFilter: <K extends keyof FilterState>(key: K, value: FilterState[K]) => void
  }
  availableBrands: string[]
  categorySpecs?: FilterSpec[]
  activeFilterCount: number
}

export default function MobileFilterDrawer({ filters, onFilterChange, availableBrands, categorySpecs, activeFilterCount }: MobileFilterDrawerProps) {
  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="outline" size="sm" className="border-[#374151] text-gray-300 hover:bg-[#1f2937] lg:hidden">
          <SlidersHorizontal className="h-4 w-4 mr-2" />
          Filters
          {activeFilterCount > 0 && (
            <span className="ml-1 bg-[#3b82f6] text-white text-xs rounded-full h-4 w-4 flex items-center justify-center">
              {activeFilterCount}
            </span>
          )}
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="w-80 bg-[#111827] border-r border-[#374151] p-0 overflow-y-auto">
        <SheetHeader className="p-4 border-b border-[#374151]">
          <SheetTitle className="text-white">Filters</SheetTitle>
        </SheetHeader>
        <div className="p-4">
          <FilterSidebar
            filters={filters}
            onFilterChange={onFilterChange}
            availableBrands={availableBrands}
            categorySpecs={categorySpecs}
          />
        </div>
      </SheetContent>
    </Sheet>
  )
}

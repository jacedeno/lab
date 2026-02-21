'use client'
import { useState } from 'react'
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { Input } from '@/components/ui/input'
import { Switch } from '@/components/ui/switch'
import { FilterState, FilterSpec } from '@/types/filters'
import { formatPrice } from '@/lib/formatters'
import { Search } from 'lucide-react'

interface FilterSidebarProps {
  filters: FilterState
  onFilterChange: {
    toggleBrand: (brand: string) => void
    toggleSpec: (key: string, value: string) => void
    setPriceRange: (min: number, max: number) => void
    setFilter: <K extends keyof FilterState>(key: K, value: FilterState[K]) => void
  }
  availableBrands: string[]
  categorySpecs?: FilterSpec[]
}

export default function FilterSidebar({ filters, onFilterChange, availableBrands, categorySpecs = [] }: FilterSidebarProps) {
  const [brandSearch, setBrandSearch] = useState('')

  const filteredBrands = availableBrands.filter(b =>
    b.toLowerCase().includes(brandSearch.toLowerCase())
  )

  return (
    <div className="w-64 shrink-0">
      <div className="bg-[#111827] border border-[#374151] rounded-xl p-4 sticky top-24">
        <h2 className="font-semibold text-white mb-4">Filters</h2>

        <Accordion type="multiple" defaultValue={['brand', 'price', 'stock']} className="space-y-1">
          {/* Brand */}
          <AccordionItem value="brand" className="border-[#374151]">
            <AccordionTrigger className="text-sm font-medium text-gray-300 hover:text-white py-2 hover:no-underline">
              Brand
            </AccordionTrigger>
            <AccordionContent>
              <div className="relative mb-2">
                <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3 w-3 text-gray-500" />
                <Input
                  type="text"
                  placeholder="Search brands..."
                  value={brandSearch}
                  onChange={(e) => setBrandSearch(e.target.value)}
                  className="pl-8 h-8 text-xs bg-[#1f2937] border-[#374151] text-gray-300 placeholder:text-gray-600"
                />
              </div>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {filteredBrands.map(brand => (
                  <div key={brand} className="flex items-center gap-2">
                    <Checkbox
                      id={`brand-${brand}`}
                      checked={filters.brands.includes(brand)}
                      onCheckedChange={() => onFilterChange.toggleBrand(brand)}
                      className="border-[#374151] data-[state=checked]:bg-[#3b82f6] data-[state=checked]:border-[#3b82f6]"
                    />
                    <Label htmlFor={`brand-${brand}`} className="text-sm text-gray-400 cursor-pointer hover:text-white">
                      {brand}
                    </Label>
                  </div>
                ))}
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Price Range */}
          <AccordionItem value="price" className="border-[#374151]">
            <AccordionTrigger className="text-sm font-medium text-gray-300 hover:text-white py-2 hover:no-underline">
              Price Range
            </AccordionTrigger>
            <AccordionContent>
              <div className="px-1 pb-2">
                <Slider
                  min={0}
                  max={10000}
                  step={50}
                  value={[filters.priceMin, filters.priceMax]}
                  onValueChange={([min, max]) => onFilterChange.setPriceRange(min, max)}
                  className="mb-3"
                />
                <div className="flex items-center justify-between text-xs text-gray-400">
                  <span>{formatPrice(filters.priceMin)}</span>
                  <span>{formatPrice(filters.priceMax)}</span>
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* In Stock */}
          <AccordionItem value="stock" className="border-[#374151]">
            <AccordionTrigger className="text-sm font-medium text-gray-300 hover:text-white py-2 hover:no-underline">
              Availability
            </AccordionTrigger>
            <AccordionContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Label className="text-sm text-gray-400">In Stock Only</Label>
                  <Switch
                    checked={filters.inStockOnly}
                    onCheckedChange={(v) => onFilterChange.setFilter('inStockOnly', v)}
                    className="data-[state=checked]:bg-[#3b82f6]"
                  />
                </div>
                <div className="flex items-center justify-between">
                  <Label className="text-sm text-gray-400">New Arrivals</Label>
                  <Switch
                    checked={filters.newArrivalsOnly}
                    onCheckedChange={(v) => onFilterChange.setFilter('newArrivalsOnly', v)}
                    className="data-[state=checked]:bg-[#3b82f6]"
                  />
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Category-specific specs */}
          {categorySpecs.map(spec => (
            <AccordionItem key={spec.key} value={spec.key} className="border-[#374151]">
              <AccordionTrigger className="text-sm font-medium text-gray-300 hover:text-white py-2 hover:no-underline">
                {spec.label}
              </AccordionTrigger>
              <AccordionContent>
                <div className="space-y-2">
                  {spec.options.map(option => (
                    <div key={option} className="flex items-center gap-2">
                      <Checkbox
                        id={`${spec.key}-${option}`}
                        checked={(filters.specs[spec.key] || []).includes(option)}
                        onCheckedChange={() => onFilterChange.toggleSpec(spec.key, option)}
                        className="border-[#374151] data-[state=checked]:bg-[#3b82f6] data-[state=checked]:border-[#3b82f6]"
                      />
                      <Label htmlFor={`${spec.key}-${option}`} className="text-sm text-gray-400 cursor-pointer hover:text-white">
                        {option}
                      </Label>
                    </div>
                  ))}
                </div>
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </div>
  )
}

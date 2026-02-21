'use client'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { SORT_OPTIONS } from '@/lib/constants'
import { SortOption } from '@/types/filters'

interface SortControlsProps {
  value: SortOption
  onChange: (value: SortOption) => void
  count: number
}

export default function SortControls({ value, onChange, count }: SortControlsProps) {
  return (
    <div className="flex items-center gap-3">
      <span className="text-sm text-gray-400 whitespace-nowrap">{count} products</span>
      <Select value={value} onValueChange={(v) => onChange(v as SortOption)}>
        <SelectTrigger className="w-48 bg-[#1f2937] border-[#374151] text-gray-300">
          <SelectValue />
        </SelectTrigger>
        <SelectContent className="bg-[#1f2937] border-[#374151]">
          {SORT_OPTIONS.map(opt => (
            <SelectItem key={opt.value} value={opt.value} className="text-gray-300 focus:bg-[#374151] focus:text-white">
              {opt.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}

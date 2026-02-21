'use client'
import { Minus, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface QuantitySelectorProps {
  value: number
  onChange: (value: number) => void
  min?: number
  max?: number
  className?: string
}

export default function QuantitySelector({ value, onChange, min = 1, max = 99, className }: QuantitySelectorProps) {
  return (
    <div className={cn('flex items-center border border-[#374151] rounded-lg overflow-hidden', className)}>
      <Button
        variant="ghost"
        size="icon"
        onClick={() => onChange(Math.max(min, value - 1))}
        disabled={value <= min}
        className="h-9 w-9 rounded-none text-gray-400 hover:text-white hover:bg-[#1f2937] disabled:opacity-40"
      >
        <Minus className="h-4 w-4" />
      </Button>
      <span className="w-12 text-center text-sm font-semibold text-white">{value}</span>
      <Button
        variant="ghost"
        size="icon"
        onClick={() => onChange(Math.min(max, value + 1))}
        disabled={value >= max}
        className="h-9 w-9 rounded-none text-gray-400 hover:text-white hover:bg-[#1f2937] disabled:opacity-40"
      >
        <Plus className="h-4 w-4" />
      </Button>
    </div>
  )
}

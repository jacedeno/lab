'use client'
import { LayoutGrid, List } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface ViewToggleProps {
  value: 'grid' | 'list'
  onChange: (value: 'grid' | 'list') => void
}

export default function ViewToggle({ value, onChange }: ViewToggleProps) {
  return (
    <div className="flex border border-[#374151] rounded-lg overflow-hidden">
      <Button
        variant="ghost"
        size="icon"
        onClick={() => onChange('grid')}
        className={cn('h-9 w-9 rounded-none', value === 'grid' ? 'bg-[#3b82f6] text-white' : 'text-gray-400 hover:text-white hover:bg-[#1f2937]')}
      >
        <LayoutGrid className="h-4 w-4" />
      </Button>
      <Button
        variant="ghost"
        size="icon"
        onClick={() => onChange('list')}
        className={cn('h-9 w-9 rounded-none', value === 'list' ? 'bg-[#3b82f6] text-white' : 'text-gray-400 hover:text-white hover:bg-[#1f2937]')}
      >
        <List className="h-4 w-4" />
      </Button>
    </div>
  )
}

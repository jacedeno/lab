'use client'
import { useState } from 'react'
import { Search } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { useRouter } from 'next/navigation'
import { cn } from '@/lib/utils'

interface SearchBarProps {
  className?: string
  placeholder?: string
  defaultValue?: string
}

export default function SearchBar({ className, placeholder = 'Search products...', defaultValue = '' }: SearchBarProps) {
  const [query, setQuery] = useState(defaultValue)
  const router = useRouter()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) router.push(`/search?q=${encodeURIComponent(query.trim())}`)
  }

  return (
    <form onSubmit={handleSubmit} className={cn('relative', className)}>
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
      <Input
        type="search"
        placeholder={placeholder}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="pl-10 bg-[#1f2937] border-[#374151] text-white placeholder:text-gray-500 focus:border-[#3b82f6] w-full"
      />
    </form>
  )
}

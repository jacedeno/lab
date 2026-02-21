import Link from 'next/link'
import { ChevronRight, Home } from 'lucide-react'
import { cn } from '@/lib/utils'

interface BreadcrumbItem {
  label: string
  href?: string
}

interface BreadcrumbProps {
  items: BreadcrumbItem[]
  className?: string
}

export default function Breadcrumb({ items, className }: BreadcrumbProps) {
  return (
    <nav className={cn('flex items-center gap-1 text-sm text-gray-500', className)}>
      <Link href="/" className="hover:text-white transition-colors flex items-center">
        <Home className="h-3.5 w-3.5" />
      </Link>
      {items.map((item, i) => (
        <span key={i} className="flex items-center gap-1">
          <ChevronRight className="h-3 w-3 text-gray-600" />
          {item.href && i < items.length - 1 ? (
            <Link href={item.href} className="hover:text-white transition-colors">{item.label}</Link>
          ) : (
            <span className={i === items.length - 1 ? 'text-white' : ''}>{item.label}</span>
          )}
        </span>
      ))}
    </nav>
  )
}

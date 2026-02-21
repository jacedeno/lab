import { cn } from '@/lib/utils'
import { LucideIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import Link from 'next/link'

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description: string
  actionLabel?: string
  actionHref?: string
  className?: string
}

export default function EmptyState({ icon: Icon, title, description, actionLabel, actionHref, className }: EmptyStateProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center py-16 text-center', className)}>
      <div className="p-4 rounded-full bg-[#1f2937] text-[#22d3ee] mb-4">
        <Icon className="h-8 w-8" />
      </div>
      <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
      <p className="text-gray-400 mb-6 max-w-sm">{description}</p>
      {actionLabel && actionHref && (
        <Button asChild className="bg-[#3b82f6] hover:bg-[#2563eb] text-white">
          <Link href={actionHref}>{actionLabel}</Link>
        </Button>
      )}
    </div>
  )
}

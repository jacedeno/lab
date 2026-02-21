import { Skeleton } from '@/components/ui/skeleton'

export function ProductCardSkeleton() {
  return (
    <div className="bg-[#111827] rounded-xl border border-[#374151] p-3">
      <Skeleton className="aspect-[4/3] w-full rounded-lg bg-[#1f2937]" />
      <div className="mt-3 space-y-2">
        <Skeleton className="h-3 w-16 bg-[#1f2937]" />
        <Skeleton className="h-4 w-full bg-[#1f2937]" />
        <Skeleton className="h-4 w-3/4 bg-[#1f2937]" />
        <Skeleton className="h-3 w-24 bg-[#1f2937]" />
        <Skeleton className="h-6 w-20 bg-[#1f2937]" />
        <Skeleton className="h-9 w-full bg-[#1f2937]" />
      </div>
    </div>
  )
}

export function ProductGridSkeleton({ count = 8 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <ProductCardSkeleton key={i} />
      ))}
    </div>
  )
}

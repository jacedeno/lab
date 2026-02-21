import { Product } from '@/types/product'
import { Separator } from '@/components/ui/separator'

interface SpecsTableProps {
  product: Product
}

export default function SpecsTable({ product }: SpecsTableProps) {
  const sortedSpecs = [...product.specs].sort((a, b) => a.sortOrder - b.sortOrder)

  // Format spec key for display
  const formatKey = (key: string) => {
    return key
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase())
  }

  return (
    <div className="bg-[#111827] border border-[#374151] rounded-xl p-6">
      <h2 className="text-lg font-bold text-white mb-4">Technical Specifications</h2>
      <div className="divide-y divide-[#374151]">
        {sortedSpecs.map((spec, i) => (
          <div key={spec.id} className="flex py-2.5">
            <span className="w-1/3 text-sm text-gray-500 shrink-0">{formatKey(spec.key)}</span>
            <span className="text-sm text-white">
              {spec.value}{spec.unit ? ` ${spec.unit}` : ''}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

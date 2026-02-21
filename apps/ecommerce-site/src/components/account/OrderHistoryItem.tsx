import { Order } from '@/types/order'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { formatDate, formatOrderId, formatPrice } from '@/lib/formatters'
import { ORDER_STATUS_COLORS, ORDER_STATUS_LABELS } from '@/lib/constants'
import { Package, ChevronRight } from 'lucide-react'
import Link from 'next/link'

interface OrderHistoryItemProps {
  order: Order
}

export default function OrderHistoryItem({ order }: OrderHistoryItemProps) {
  return (
    <div className="bg-[#111827] border border-[#374151] rounded-xl p-4">
      <div className="flex items-start justify-between gap-4 mb-3">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-bold text-white">{formatOrderId(order.id)}</span>
            <Badge className={ORDER_STATUS_COLORS[order.status]}>{ORDER_STATUS_LABELS[order.status]}</Badge>
          </div>
          <p className="text-xs text-gray-500 mt-0.5">Placed on {formatDate(order.createdAt)}</p>
        </div>
        <span className="font-bold text-white">{formatPrice(order.total)}</span>
      </div>

      <Separator className="bg-[#374151] mb-3" />

      <div className="flex items-center gap-2 text-sm text-gray-400">
        <Package className="h-4 w-4 text-[#22d3ee]" />
        <span>{order.items.length} item{order.items.length !== 1 ? 's' : ''}</span>
        <span className="text-gray-600">·</span>
        <span>{order.items.map(i => i.productName).join(', ').slice(0, 60)}...</span>
      </div>

      <div className="flex gap-2 mt-3">
        <Button variant="outline" size="sm" className="border-[#374151] text-gray-300 hover:bg-[#1f2937]" asChild>
          <Link href="#">
            View Details <ChevronRight className="h-4 w-4 ml-1" />
          </Link>
        </Button>
        {order.status === 'DELIVERED' && (
          <Button variant="outline" size="sm" className="border-[#374151] text-gray-300 hover:bg-[#1f2937]">
            Reorder
          </Button>
        )}
      </div>
    </div>
  )
}

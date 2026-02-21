import OrderHistoryItem from '@/components/account/OrderHistoryItem'
import EmptyState from '@/components/shared/EmptyState'
import { Package } from 'lucide-react'
import { Order } from '@/types/order'

// Mock orders for display
const mockOrders: Order[] = [
  {
    id: 'ord-abc123def456',
    userId: 'user-1',
    shippingAddress: {
      id: 'addr-1',
      userId: 'user-1',
      label: 'Home',
      line1: '123 Main St',
      city: 'San Francisco',
      state: 'CA',
      postalCode: '94102',
      country: 'US',
      isDefault: true,
    },
    status: 'DELIVERED',
    subtotal: 2499,
    shippingCost: 0,
    tax: 199.92,
    total: 2698.92,
    items: [
      {
        id: 'oi-1',
        productId: 'prod-1',
        product: {} as any,
        quantity: 1,
        unitPrice: 2499,
        totalPrice: 2499,
        productName: 'GeekEnd Pro Tower X1',
      },
    ],
    createdAt: '2026-01-15T10:00:00Z',
    updatedAt: '2026-01-20T14:00:00Z',
  },
  {
    id: 'ord-xyz789ghi012',
    userId: 'user-1',
    shippingAddress: {
      id: 'addr-1',
      userId: 'user-1',
      label: 'Home',
      line1: '123 Main St',
      city: 'San Francisco',
      state: 'CA',
      postalCode: '94102',
      country: 'US',
      isDefault: true,
    },
    status: 'PROCESSING',
    subtotal: 1598,
    shippingCost: 0,
    tax: 127.84,
    total: 1725.84,
    items: [
      {
        id: 'oi-2',
        productId: 'prod-14',
        product: {} as any,
        quantity: 1,
        unitPrice: 159,
        totalPrice: 159,
        productName: 'Logitech G Pro X Superlight 2',
      },
      {
        id: 'oi-3',
        productId: 'prod-11',
        product: {} as any,
        quantity: 1,
        unitPrice: 1439,
        totalPrice: 1439,
        productName: 'NVIDIA GeForce RTX 4090',
      },
    ],
    createdAt: '2026-02-10T08:00:00Z',
    updatedAt: '2026-02-10T09:00:00Z',
  },
]

export default function OrdersPage() {
  return (
    <div className="w-full max-w-2xl">
      <h1 className="text-2xl font-bold text-white mb-6">Order History</h1>
      {mockOrders.length > 0 ? (
        <div className="space-y-4">
          {mockOrders.map(order => (
            <OrderHistoryItem key={order.id} order={order} />
          ))}
        </div>
      ) : (
        <EmptyState
          icon={Package}
          title="No orders yet"
          description="Your order history will appear here once you make your first purchase."
          actionLabel="Start Shopping"
          actionHref="/products"
        />
      )}
    </div>
  )
}

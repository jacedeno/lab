'use client'
import CartItem from '@/components/cart/CartItem'
import CartSummary from '@/components/cart/CartSummary'
import EmptyCart from '@/components/cart/EmptyCart'
import Breadcrumb from '@/components/shared/Breadcrumb'
import { useCart } from '@/hooks/useCart'

export default function CartPage() {
  const { items, subtotal } = useCart()

  return (
    <div className="container mx-auto px-4 py-8">
      <Breadcrumb items={[{ label: 'Shopping Cart' }]} className="mb-6" />
      <h1 className="text-2xl font-bold text-white mb-6">Shopping Cart</h1>

      {items.length === 0 ? (
        <EmptyCart />
      ) : (
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Cart items */}
          <div className="lg:col-span-2 space-y-3">
            {items.map(item => (
              <CartItem key={item.product.id} item={item} />
            ))}
          </div>

          {/* Summary sidebar */}
          <div>
            <CartSummary subtotal={subtotal} />
          </div>
        </div>
      )}
    </div>
  )
}

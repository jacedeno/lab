'use client'
import Image from 'next/image'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { ShieldCheck } from 'lucide-react'
import { CartItem } from '@/types/cart'
import { ShippingFormData, PaymentFormData } from '@/lib/validators'
import { formatPrice } from '@/lib/formatters'
import { siteConfig } from '@/config/site'

interface OrderReviewProps {
  items: CartItem[]
  shipping: ShippingFormData
  payment: PaymentFormData
  onBack: () => void
  onPlaceOrder: () => void
}

export default function OrderReview({ items, shipping, payment, onBack, onPlaceOrder }: OrderReviewProps) {
  const subtotal = items.reduce((s, i) => s + i.product.price * i.quantity, 0)
  const shippingCost = subtotal >= siteConfig.shipping.freeThreshold ? 0 : siteConfig.shipping.standardRate
  const tax = subtotal * siteConfig.tax.rate
  const total = subtotal + shippingCost + tax

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-bold text-white">Review Your Order</h2>

      {/* Items */}
      <div className="bg-[#1f2937] rounded-xl p-4 space-y-3">
        {items.map(item => (
          <div key={item.product.id} className="flex gap-3 items-center">
            <div className="relative w-12 h-12 rounded-lg overflow-hidden bg-[#374151] shrink-0">
              <Image src={item.product.thumbnailUrl} alt={item.product.name} fill className="object-cover" sizes="48px" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-white font-medium line-clamp-1">{item.product.name}</p>
              <p className="text-xs text-gray-500">Qty: {item.quantity}</p>
            </div>
            <span className="text-sm font-semibold text-white">{formatPrice(item.product.price * item.quantity)}</span>
          </div>
        ))}
      </div>

      {/* Shipping info */}
      <div className="bg-[#1f2937] rounded-xl p-4">
        <p className="text-xs text-gray-500 font-medium uppercase tracking-wider mb-2">Shipping To</p>
        <p className="text-sm text-white">{shipping.firstName} {shipping.lastName}</p>
        <p className="text-sm text-gray-400">{shipping.address}</p>
        <p className="text-sm text-gray-400">{shipping.city}, {shipping.state} {shipping.zipCode}</p>
      </div>

      {/* Payment info */}
      <div className="bg-[#1f2937] rounded-xl p-4">
        <p className="text-xs text-gray-500 font-medium uppercase tracking-wider mb-2">Payment</p>
        <p className="text-sm text-white">Card ending in {payment.cardNumber.slice(-4)}</p>
      </div>

      {/* Totals */}
      <div className="space-y-2 text-sm">
        <div className="flex justify-between text-gray-400"><span>Subtotal</span><span className="text-white">{formatPrice(subtotal)}</span></div>
        <div className="flex justify-between text-gray-400"><span>Shipping</span><span className={shippingCost === 0 ? 'text-green-400' : 'text-white'}>{shippingCost === 0 ? 'FREE' : formatPrice(shippingCost)}</span></div>
        <div className="flex justify-between text-gray-400"><span>Tax</span><span className="text-white">{formatPrice(tax)}</span></div>
        <Separator className="bg-[#374151]" />
        <div className="flex justify-between font-bold text-white text-base"><span>Total</span><span>{formatPrice(total)}</span></div>
      </div>

      <div className="flex gap-3">
        <Button type="button" variant="outline" size="lg" onClick={onBack} className="flex-1 border-[#374151] text-gray-300 hover:bg-[#1f2937]">
          Back
        </Button>
        <Button size="lg" onClick={onPlaceOrder} className="flex-1 bg-[#3b82f6] hover:bg-[#2563eb] text-white shadow-glow-blue">
          <ShieldCheck className="mr-2 h-4 w-4" />
          Place Order
        </Button>
      </div>
    </div>
  )
}

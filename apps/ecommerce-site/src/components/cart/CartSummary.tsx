'use client'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { Input } from '@/components/ui/input'
import { ArrowRight, Tag } from 'lucide-react'
import { formatPrice } from '@/lib/formatters'
import { siteConfig } from '@/config/site'

interface CartSummaryProps {
  subtotal: number
  showCheckoutButton?: boolean
}

export default function CartSummary({ subtotal, showCheckoutButton = true }: CartSummaryProps) {
  const shipping = subtotal >= siteConfig.shipping.freeThreshold ? 0 : siteConfig.shipping.standardRate
  const tax = subtotal * siteConfig.tax.rate
  const total = subtotal + shipping + tax

  return (
    <div className="bg-[#111827] border border-[#374151] rounded-xl p-5 sticky top-24">
      <h2 className="font-bold text-white mb-4">Order Summary</h2>

      <div className="space-y-3 text-sm">
        <div className="flex justify-between text-gray-400">
          <span>Subtotal</span>
          <span className="text-white">{formatPrice(subtotal)}</span>
        </div>
        <div className="flex justify-between text-gray-400">
          <span>Shipping</span>
          <span className={shipping === 0 ? 'text-green-400' : 'text-white'}>
            {shipping === 0 ? 'FREE' : formatPrice(shipping)}
          </span>
        </div>
        <div className="flex justify-between text-gray-400">
          <span>Tax (8%)</span>
          <span className="text-white">{formatPrice(tax)}</span>
        </div>
        {subtotal < siteConfig.shipping.freeThreshold && (
          <p className="text-xs text-[#22d3ee] bg-[#22d3ee]/10 rounded-lg px-3 py-2">
            Add {formatPrice(siteConfig.shipping.freeThreshold - subtotal)} more for free shipping!
          </p>
        )}
      </div>

      <Separator className="my-4 bg-[#374151]" />

      <div className="flex justify-between font-bold text-white mb-5">
        <span>Total</span>
        <span className="text-xl">{formatPrice(total)}</span>
      </div>

      {/* Coupon */}
      <div className="flex gap-2 mb-4">
        <div className="relative flex-1">
          <Tag className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
          <Input
            placeholder="Coupon code"
            className="pl-8 h-9 bg-[#1f2937] border-[#374151] text-gray-300 placeholder:text-gray-600 text-sm"
          />
        </div>
        <Button variant="outline" size="sm" className="border-[#374151] text-gray-300 hover:bg-[#1f2937] h-9">
          Apply
        </Button>
      </div>

      {showCheckoutButton && (
        <Button asChild size="lg" className="w-full bg-[#3b82f6] hover:bg-[#2563eb] text-white shadow-glow-blue">
          <Link href="/checkout">
            Proceed to Checkout <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </Button>
      )}

      <p className="text-xs text-gray-600 text-center mt-3">
        Secure checkout with 256-bit SSL encryption
      </p>
    </div>
  )
}

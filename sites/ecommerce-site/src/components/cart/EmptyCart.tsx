import Link from 'next/link'
import { ShoppingCart, ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function EmptyCart() {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <div className="p-6 rounded-full bg-[#1f2937] text-[#374151] mb-6">
        <ShoppingCart className="h-12 w-12" />
      </div>
      <h2 className="text-2xl font-bold text-white mb-3">Your cart is empty</h2>
      <p className="text-gray-400 mb-8 max-w-sm">
        Looks like you have not added anything to your cart yet. Start exploring our products!
      </p>
      <Button asChild size="lg" className="bg-[#3b82f6] hover:bg-[#2563eb] text-white">
        <Link href="/products">
          Shop Now <ArrowRight className="ml-2 h-4 w-4" />
        </Link>
      </Button>
    </div>
  )
}

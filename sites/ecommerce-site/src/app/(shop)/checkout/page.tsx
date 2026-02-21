'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import CheckoutStepper from '@/components/checkout/CheckoutStepper'
import ShippingForm from '@/components/checkout/ShippingForm'
import PaymentForm from '@/components/checkout/PaymentForm'
import OrderReview from '@/components/checkout/OrderReview'
import CartSummary from '@/components/cart/CartSummary'
import { useCart } from '@/hooks/useCart'
import { ShippingFormData, PaymentFormData } from '@/lib/validators'
import { CheckCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import Link from 'next/link'

export default function CheckoutPage() {
  const [step, setStep] = useState(1)
  const [shippingData, setShippingData] = useState<ShippingFormData | null>(null)
  const [paymentData, setPaymentData] = useState<PaymentFormData | null>(null)
  const [orderPlaced, setOrderPlaced] = useState(false)
  const { items, subtotal, clearCart } = useCart()
  const router = useRouter()

  const handlePlaceOrder = () => {
    clearCart()
    setOrderPlaced(true)
  }

  if (orderPlaced) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <div className="max-w-md mx-auto">
          <div className="flex justify-center mb-6">
            <div className="p-4 rounded-full bg-green-500/20 text-green-400">
              <CheckCircle className="h-16 w-16" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-white mb-3">Order Placed!</h1>
          <p className="text-gray-400 mb-8">
            Thank you for your order. We will send a confirmation email shortly.
          </p>
          <div className="flex gap-3 justify-center">
            <Button asChild className="bg-[#3b82f6] hover:bg-[#2563eb] text-white">
              <Link href="/account/orders">View Orders</Link>
            </Button>
            <Button asChild variant="outline" className="border-[#374151] text-gray-300 hover:bg-[#1f2937]">
              <Link href="/products">Continue Shopping</Link>
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-white mb-6">Checkout</h1>
      <CheckoutStepper currentStep={step} />

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Form area */}
        <div className="lg:col-span-2 bg-[#111827] border border-[#374151] rounded-xl p-6">
          {step === 1 && (
            <ShippingForm
              onNext={(data) => { setShippingData(data); setStep(2) }}
              defaultValues={shippingData || undefined}
            />
          )}
          {step === 2 && (
            <PaymentForm
              onNext={(data) => { setPaymentData(data); setStep(3) }}
              onBack={() => setStep(1)}
            />
          )}
          {step === 3 && shippingData && paymentData && (
            <OrderReview
              items={items}
              shipping={shippingData}
              payment={paymentData}
              onBack={() => setStep(2)}
              onPlaceOrder={handlePlaceOrder}
            />
          )}
        </div>

        {/* Order summary */}
        <div>
          <CartSummary subtotal={subtotal} showCheckoutButton={false} />
        </div>
      </div>
    </div>
  )
}

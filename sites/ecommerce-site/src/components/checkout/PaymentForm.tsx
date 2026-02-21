'use client'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { ArrowRight, Lock, CreditCard } from 'lucide-react'
import { paymentSchema, PaymentFormData } from '@/lib/validators'

interface PaymentFormProps {
  onNext: (data: PaymentFormData) => void
  onBack: () => void
}

export default function PaymentForm({ onNext, onBack }: PaymentFormProps) {
  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm<PaymentFormData>({
    resolver: zodResolver(paymentSchema),
    defaultValues: { billingAddressSame: true },
  })

  return (
    <form onSubmit={handleSubmit(onNext)} className="space-y-4">
      <h2 className="text-lg font-bold text-white mb-4">Payment Information</h2>

      <div className="flex items-center gap-2 p-3 bg-green-500/10 border border-green-500/20 rounded-lg text-green-400 text-sm">
        <Lock className="h-4 w-4 shrink-0" />
        Your payment information is encrypted and secure.
      </div>

      <div>
        <Label className="text-gray-400 text-sm">Card Number</Label>
        <div className="relative mt-1">
          <CreditCard className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
          <Input
            {...register('cardNumber')}
            placeholder="1234 5678 9012 3456"
            className="pl-10 bg-[#1f2937] border-[#374151] text-white"
          />
        </div>
        {errors.cardNumber && <p className="text-red-400 text-xs mt-1">{errors.cardNumber.message}</p>}
      </div>

      <div>
        <Label className="text-gray-400 text-sm">Cardholder Name</Label>
        <Input {...register('cardHolder')} placeholder="John Doe" className="mt-1 bg-[#1f2937] border-[#374151] text-white" />
        {errors.cardHolder && <p className="text-red-400 text-xs mt-1">{errors.cardHolder.message}</p>}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label className="text-gray-400 text-sm">Expiry Date</Label>
          <Input {...register('expiryDate')} placeholder="MM/YY" className="mt-1 bg-[#1f2937] border-[#374151] text-white" />
          {errors.expiryDate && <p className="text-red-400 text-xs mt-1">{errors.expiryDate.message}</p>}
        </div>
        <div>
          <Label className="text-gray-400 text-sm">CVV</Label>
          <Input {...register('cvv')} placeholder="123" className="mt-1 bg-[#1f2937] border-[#374151] text-white" />
          {errors.cvv && <p className="text-red-400 text-xs mt-1">{errors.cvv.message}</p>}
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Checkbox
          id="billingAddressSame"
          checked={watch('billingAddressSame')}
          onCheckedChange={(v) => setValue('billingAddressSame', !!v)}
          className="border-[#374151] data-[state=checked]:bg-[#3b82f6] data-[state=checked]:border-[#3b82f6]"
        />
        <Label htmlFor="billingAddressSame" className="text-sm text-gray-400 cursor-pointer">
          Billing address same as shipping
        </Label>
      </div>

      <div className="flex gap-3">
        <Button type="button" variant="outline" size="lg" onClick={onBack} className="flex-1 border-[#374151] text-gray-300 hover:bg-[#1f2937]">
          Back
        </Button>
        <Button type="submit" size="lg" className="flex-1 bg-[#3b82f6] hover:bg-[#2563eb] text-white">
          Review Order <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      </div>
    </form>
  )
}

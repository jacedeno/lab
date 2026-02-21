'use client'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { ArrowRight } from 'lucide-react'
import { shippingSchema, ShippingFormData } from '@/lib/validators'

const US_STATES = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']

interface ShippingFormProps {
  onNext: (data: ShippingFormData) => void
  defaultValues?: Partial<ShippingFormData>
}

export default function ShippingForm({ onNext, defaultValues }: ShippingFormProps) {
  const { register, handleSubmit, setValue, formState: { errors } } = useForm<ShippingFormData>({
    resolver: zodResolver(shippingSchema),
    defaultValues,
  })

  return (
    <form onSubmit={handleSubmit(onNext)} className="space-y-4">
      <h2 className="text-lg font-bold text-white mb-4">Shipping Information</h2>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label className="text-gray-400 text-sm">First Name</Label>
          <Input {...register('firstName')} className="mt-1 bg-[#1f2937] border-[#374151] text-white" />
          {errors.firstName && <p className="text-red-400 text-xs mt-1">{errors.firstName.message}</p>}
        </div>
        <div>
          <Label className="text-gray-400 text-sm">Last Name</Label>
          <Input {...register('lastName')} className="mt-1 bg-[#1f2937] border-[#374151] text-white" />
          {errors.lastName && <p className="text-red-400 text-xs mt-1">{errors.lastName.message}</p>}
        </div>
      </div>

      <div>
        <Label className="text-gray-400 text-sm">Email</Label>
        <Input {...register('email')} type="email" className="mt-1 bg-[#1f2937] border-[#374151] text-white" />
        {errors.email && <p className="text-red-400 text-xs mt-1">{errors.email.message}</p>}
      </div>

      <div>
        <Label className="text-gray-400 text-sm">Phone</Label>
        <Input {...register('phone')} type="tel" className="mt-1 bg-[#1f2937] border-[#374151] text-white" />
        {errors.phone && <p className="text-red-400 text-xs mt-1">{errors.phone.message}</p>}
      </div>

      <div>
        <Label className="text-gray-400 text-sm">Address</Label>
        <Input {...register('address')} className="mt-1 bg-[#1f2937] border-[#374151] text-white" />
        {errors.address && <p className="text-red-400 text-xs mt-1">{errors.address.message}</p>}
      </div>

      <div>
        <Label className="text-gray-400 text-sm">Apartment, suite, etc. (optional)</Label>
        <Input {...register('address2')} className="mt-1 bg-[#1f2937] border-[#374151] text-white" />
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2">
          <Label className="text-gray-400 text-sm">City</Label>
          <Input {...register('city')} className="mt-1 bg-[#1f2937] border-[#374151] text-white" />
          {errors.city && <p className="text-red-400 text-xs mt-1">{errors.city.message}</p>}
        </div>
        <div>
          <Label className="text-gray-400 text-sm">ZIP Code</Label>
          <Input {...register('zipCode')} className="mt-1 bg-[#1f2937] border-[#374151] text-white" />
          {errors.zipCode && <p className="text-red-400 text-xs mt-1">{errors.zipCode.message}</p>}
        </div>
      </div>

      <div>
        <Label className="text-gray-400 text-sm">State</Label>
        <Select onValueChange={(v) => setValue('state', v)}>
          <SelectTrigger className="mt-1 bg-[#1f2937] border-[#374151] text-gray-300">
            <SelectValue placeholder="Select state" />
          </SelectTrigger>
          <SelectContent className="bg-[#1f2937] border-[#374151] max-h-48">
            {US_STATES.map(s => (
              <SelectItem key={s} value={s} className="text-gray-300 focus:bg-[#374151] focus:text-white">{s}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        {errors.state && <p className="text-red-400 text-xs mt-1">{errors.state.message}</p>}
        <input type="hidden" {...register('state')} />
        <input type="hidden" {...register('country')} value="US" />
      </div>

      <Button type="submit" size="lg" className="w-full bg-[#3b82f6] hover:bg-[#2563eb] text-white mt-2">
        Continue to Payment <ArrowRight className="ml-2 h-4 w-4" />
      </Button>
    </form>
  )
}

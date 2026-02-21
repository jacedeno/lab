'use client'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { registerSchema, RegisterFormData } from '@/lib/validators'
import { User, Mail, Lock, ArrowRight } from 'lucide-react'

export default function RegisterForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  })

  const onSubmit = (data: RegisterFormData) => {
    console.log('Register:', data)
    // UI only — no backend
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <Label className="text-gray-400 text-sm">Full Name</Label>
        <div className="relative mt-1">
          <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
          <Input {...register('name')} placeholder="John Doe" className="pl-10 bg-[#1f2937] border-[#374151] text-white placeholder:text-gray-600" />
        </div>
        {errors.name && <p className="text-red-400 text-xs mt-1">{errors.name.message}</p>}
      </div>

      <div>
        <Label className="text-gray-400 text-sm">Email Address</Label>
        <div className="relative mt-1">
          <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
          <Input {...register('email')} type="email" placeholder="your@email.com" className="pl-10 bg-[#1f2937] border-[#374151] text-white placeholder:text-gray-600" />
        </div>
        {errors.email && <p className="text-red-400 text-xs mt-1">{errors.email.message}</p>}
      </div>

      <div>
        <Label className="text-gray-400 text-sm">Password</Label>
        <div className="relative mt-1">
          <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
          <Input {...register('password')} type="password" placeholder="Min. 8 characters" className="pl-10 bg-[#1f2937] border-[#374151] text-white" />
        </div>
        {errors.password && <p className="text-red-400 text-xs mt-1">{errors.password.message}</p>}
      </div>

      <div>
        <Label className="text-gray-400 text-sm">Confirm Password</Label>
        <div className="relative mt-1">
          <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
          <Input {...register('confirmPassword')} type="password" placeholder="Re-enter password" className="pl-10 bg-[#1f2937] border-[#374151] text-white" />
        </div>
        {errors.confirmPassword && <p className="text-red-400 text-xs mt-1">{errors.confirmPassword.message}</p>}
      </div>

      <Button type="submit" size="lg" className="w-full bg-[#3b82f6] hover:bg-[#2563eb] text-white shadow-glow-blue">
        Create Account <ArrowRight className="ml-2 h-4 w-4" />
      </Button>
    </form>
  )
}

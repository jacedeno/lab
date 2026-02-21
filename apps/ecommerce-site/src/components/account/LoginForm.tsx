'use client'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { loginSchema, LoginFormData } from '@/lib/validators'
import { Mail, Lock, ArrowRight } from 'lucide-react'

export default function LoginForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = (data: LoginFormData) => {
    console.log('Login:', data)
    // UI only — no backend
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <Label className="text-gray-400 text-sm">Email Address</Label>
        <div className="relative mt-1">
          <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
          <Input {...register('email')} type="email" placeholder="your@email.com" className="pl-10 bg-[#1f2937] border-[#374151] text-white placeholder:text-gray-600" />
        </div>
        {errors.email && <p className="text-red-400 text-xs mt-1">{errors.email.message}</p>}
      </div>

      <div>
        <div className="flex items-center justify-between mb-1">
          <Label className="text-gray-400 text-sm">Password</Label>
          <a href="#" className="text-xs text-[#3b82f6] hover:text-[#60a5fa]">Forgot password?</a>
        </div>
        <div className="relative">
          <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
          <Input {...register('password')} type="password" placeholder="••••••••" className="pl-10 bg-[#1f2937] border-[#374151] text-white" />
        </div>
        {errors.password && <p className="text-red-400 text-xs mt-1">{errors.password.message}</p>}
      </div>

      <Button type="submit" size="lg" className="w-full bg-[#3b82f6] hover:bg-[#2563eb] text-white shadow-glow-blue">
        Sign In <ArrowRight className="ml-2 h-4 w-4" />
      </Button>
    </form>
  )
}

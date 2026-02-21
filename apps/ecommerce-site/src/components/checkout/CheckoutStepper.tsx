import { Check } from 'lucide-react'
import { cn } from '@/lib/utils'

const STEPS = [
  { id: 1, label: 'Shipping' },
  { id: 2, label: 'Payment' },
  { id: 3, label: 'Review' },
]

interface CheckoutStepperProps {
  currentStep: number
}

export default function CheckoutStepper({ currentStep }: CheckoutStepperProps) {
  return (
    <div className="flex items-center justify-center mb-8">
      {STEPS.map((step, i) => (
        <div key={step.id} className="flex items-center">
          {/* Step circle */}
          <div className="flex flex-col items-center">
            <div className={cn(
              'w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold transition-all',
              step.id < currentStep
                ? 'bg-green-500 text-white'
                : step.id === currentStep
                ? 'bg-[#3b82f6] text-white shadow-glow-blue'
                : 'bg-[#1f2937] text-gray-500 border border-[#374151]'
            )}>
              {step.id < currentStep ? <Check className="h-4 w-4" /> : step.id}
            </div>
            <span className={cn('text-xs mt-1 whitespace-nowrap', step.id === currentStep ? 'text-white' : 'text-gray-500')}>
              {step.label}
            </span>
          </div>
          {/* Connector */}
          {i < STEPS.length - 1 && (
            <div className={cn('h-0.5 w-16 sm:w-24 mx-2 mb-4', step.id < currentStep ? 'bg-green-500' : 'bg-[#374151]')} />
          )}
        </div>
      ))}
    </div>
  )
}

'use client'
import { useState } from 'react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Mail, ArrowRight, Check } from 'lucide-react'

export default function Newsletter() {
  const [email, setEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (email) setSubmitted(true)
  }

  return (
    <section className="py-12 bg-gradient-to-r from-[#111827] via-[#1f2937] to-[#111827] border-y border-[#374151]">
      <div className="container mx-auto px-4">
        <div className="max-w-2xl mx-auto text-center">
          <div className="inline-flex p-3 rounded-full bg-[#3b82f6]/10 text-[#3b82f6] mb-4">
            <Mail className="h-6 w-6" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Stay in the Loop</h2>
          <p className="text-gray-400 mb-6">
            Get exclusive deals, new product alerts, and tech tips delivered to your inbox.
          </p>
          {submitted ? (
            <div className="flex items-center justify-center gap-2 text-[#22d3ee]">
              <Check className="h-5 w-5" />
              <span>Thank you! You&apos;re subscribed.</span>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
              <Input
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="flex-1 bg-[#1f2937] border-[#374151] text-white placeholder:text-gray-500 focus:border-[#3b82f6]"
              />
              <Button type="submit" className="bg-[#3b82f6] hover:bg-[#2563eb] text-white">
                Subscribe <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </form>
          )}
          <p className="text-xs text-gray-600 mt-3">No spam, unsubscribe any time.</p>
        </div>
      </div>
    </section>
  )
}

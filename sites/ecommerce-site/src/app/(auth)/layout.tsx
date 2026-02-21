import Link from 'next/link'
import { Zap } from 'lucide-react'

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[#030712] flex flex-col">
      {/* Simple header */}
      <header className="border-b border-[#374151] px-4 h-14 flex items-center">
        <Link href="/" className="flex items-center gap-2">
          <Zap className="h-5 w-5 text-[#22d3ee]" />
          <span className="font-bold bg-gradient-to-r from-[#3b82f6] to-[#22d3ee] bg-clip-text text-transparent">
            GeekendZone
          </span>
        </Link>
      </header>
      <div className="flex-1 flex items-center justify-center px-4 py-12">
        {children}
      </div>
    </div>
  )
}

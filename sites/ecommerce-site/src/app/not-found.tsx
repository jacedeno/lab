import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Home, Search } from 'lucide-react'

export default function NotFound() {
  return (
    <div className="min-h-screen bg-[#030712] flex items-center justify-center px-4">
      <div className="text-center">
        <h1 className="text-8xl font-black text-[#3b82f6] mb-4">404</h1>
        <h2 className="text-2xl font-bold text-white mb-3">Page Not Found</h2>
        <p className="text-gray-400 mb-8 max-w-sm">
          The page you&apos;re looking for doesn&apos;t exist or has been moved.
        </p>
        <div className="flex gap-3 justify-center">
          <Button asChild className="bg-[#3b82f6] hover:bg-[#2563eb] text-white">
            <Link href="/"><Home className="mr-2 h-4 w-4" />Go Home</Link>
          </Button>
          <Button asChild variant="outline" className="border-[#374151] text-gray-300 hover:bg-[#1f2937]">
            <Link href="/products"><Search className="mr-2 h-4 w-4" />Browse Products</Link>
          </Button>
        </div>
      </div>
    </div>
  )
}

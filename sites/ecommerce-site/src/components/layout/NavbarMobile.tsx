'use client'
import Link from 'next/link'
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { Separator } from '@/components/ui/separator'
import { Zap, ChevronRight } from 'lucide-react'
import { mainNavItems } from '@/config/navigation'

interface NavbarMobileProps {
  open: boolean
  onClose: () => void
}

export default function NavbarMobile({ open, onClose }: NavbarMobileProps) {
  return (
    <Sheet open={open} onOpenChange={onClose}>
      <SheetContent side="left" className="w-72 bg-[#111827] border-r border-[#374151] p-0">
        <SheetHeader className="p-4 border-b border-[#374151]">
          <SheetTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-[#22d3ee]" />
            <span className="bg-gradient-to-r from-[#3b82f6] to-[#22d3ee] bg-clip-text text-transparent font-bold">
              GeekendZone
            </span>
          </SheetTitle>
        </SheetHeader>
        <nav className="p-2">
          <p className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">Categories</p>
          {mainNavItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              onClick={onClose}
              className="flex items-center justify-between px-3 py-2.5 text-sm text-gray-300 hover:text-white hover:bg-[#1f2937] rounded-lg transition-colors"
            >
              {item.label}
              <ChevronRight className="h-4 w-4 text-gray-500" />
            </Link>
          ))}
          <Separator className="my-2 bg-[#374151]" />
          <Link href="/account" onClick={onClose} className="flex items-center justify-between px-3 py-2.5 text-sm text-gray-300 hover:text-white hover:bg-[#1f2937] rounded-lg transition-colors">
            My Account <ChevronRight className="h-4 w-4 text-gray-500" />
          </Link>
          <Link href="/account/orders" onClick={onClose} className="flex items-center justify-between px-3 py-2.5 text-sm text-gray-300 hover:text-white hover:bg-[#1f2937] rounded-lg transition-colors">
            My Orders <ChevronRight className="h-4 w-4 text-gray-500" />
          </Link>
          <Link href="/cart" onClick={onClose} className="flex items-center justify-between px-3 py-2.5 text-sm text-gray-300 hover:text-white hover:bg-[#1f2937] rounded-lg transition-colors">
            Shopping Cart <ChevronRight className="h-4 w-4 text-gray-500" />
          </Link>
        </nav>
      </SheetContent>
    </Sheet>
  )
}

'use client'
import Link from 'next/link'
import { useState } from 'react'
import { ShoppingCart, Heart, User, Search, Menu, Zap } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { useCart } from '@/hooks/useCart'
import { useWishlist } from '@/hooks/useWishlist'
import { mainNavItems } from '@/config/navigation'
import { useRouter } from 'next/navigation'
import NavbarMobile from './NavbarMobile'

export default function Navbar() {
  const { totalItems } = useCart()
  const { count: wishlistCount } = useWishlist()
  const [searchQuery, setSearchQuery] = useState('')
  const [mobileOpen, setMobileOpen] = useState(false)
  const router = useRouter()

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`)
    }
  }

  return (
    <>
      <header className="sticky top-0 z-50 bg-[#030712]/95 backdrop-blur-md border-b border-[#374151]">
        {/* Main nav row */}
        <div className="container mx-auto px-4">
          <div className="flex items-center h-16 gap-4">
            {/* Mobile menu button */}
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden text-gray-400 hover:text-white"
              onClick={() => setMobileOpen(true)}
            >
              <Menu className="h-5 w-5" />
            </Button>

            {/* Logo */}
            <Link href="/" className="flex items-center gap-2 shrink-0">
              <Zap className="h-6 w-6 text-[#22d3ee]" />
              <span className="text-xl font-bold bg-gradient-to-r from-[#3b82f6] to-[#22d3ee] bg-clip-text text-transparent">
                GeekendZone
              </span>
            </Link>

            {/* Search bar - desktop */}
            <form onSubmit={handleSearch} className="hidden lg:flex flex-1 max-w-xl mx-auto">
              <div className="relative w-full">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  type="search"
                  placeholder="Search products..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 bg-[#1f2937] border-[#374151] text-white placeholder:text-gray-500 focus:border-[#3b82f6] focus:ring-[#3b82f6]/20 w-full"
                />
              </div>
            </form>

            {/* Icons */}
            <div className="flex items-center gap-1 ml-auto">
              {/* Mobile search */}
              <Button variant="ghost" size="icon" className="lg:hidden text-gray-400 hover:text-white" asChild>
                <Link href="/search"><Search className="h-5 w-5" /></Link>
              </Button>

              {/* Wishlist */}
              <Button variant="ghost" size="icon" className="relative text-gray-400 hover:text-white" asChild>
                <Link href="/account">
                  <Heart className="h-5 w-5" />
                  {wishlistCount > 0 && (
                    <Badge className="absolute -top-1 -right-1 h-4 w-4 p-0 flex items-center justify-center text-[10px] bg-[#3b82f6] border-0">
                      {wishlistCount}
                    </Badge>
                  )}
                </Link>
              </Button>

              {/* Cart */}
              <Button variant="ghost" size="icon" className="relative text-gray-400 hover:text-white" asChild>
                <Link href="/cart">
                  <ShoppingCart className="h-5 w-5" />
                  {totalItems > 0 && (
                    <Badge className="absolute -top-1 -right-1 h-4 w-4 p-0 flex items-center justify-center text-[10px] bg-[#3b82f6] border-0">
                      {totalItems > 9 ? '9+' : totalItems}
                    </Badge>
                  )}
                </Link>
              </Button>

              {/* Account */}
              <Button variant="ghost" size="icon" className="text-gray-400 hover:text-white" asChild>
                <Link href="/account"><User className="h-5 w-5" /></Link>
              </Button>
            </div>
          </div>
        </div>

        {/* Category nav - desktop only */}
        <nav className="hidden lg:block border-t border-[#374151]/50">
          <div className="container mx-auto px-4">
            <div className="flex items-center gap-1 h-10">
              {mainNavItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="px-3 py-1.5 text-sm text-gray-400 hover:text-white hover:bg-[#1f2937] rounded-md transition-colors"
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </div>
        </nav>
      </header>

      {/* Mobile Nav Drawer */}
      <NavbarMobile open={mobileOpen} onClose={() => setMobileOpen(false)} />
    </>
  )
}

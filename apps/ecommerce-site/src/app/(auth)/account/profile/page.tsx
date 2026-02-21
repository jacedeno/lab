import ProfileCard from '@/components/account/ProfileCard'
import Link from 'next/link'
import { ChevronRight } from 'lucide-react'

export default function ProfilePage() {
  return (
    <div className="w-full max-w-2xl">
      <nav className="flex gap-2 mb-6 text-sm">
        {[
          { label: 'Profile', href: '/account/profile' },
          { label: 'Orders', href: '/account/orders' },
        ].map(item => (
          <Link key={item.href} href={item.href} className="text-[#3b82f6] hover:text-[#60a5fa] flex items-center gap-1">
            {item.label} <ChevronRight className="h-3.5 w-3.5" />
          </Link>
        ))}
      </nav>
      <ProfileCard />
    </div>
  )
}

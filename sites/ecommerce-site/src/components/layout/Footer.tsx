import Link from 'next/link'
import { Zap, Twitter, Github, Linkedin } from 'lucide-react'
import { Separator } from '@/components/ui/separator'
import { footerLinks } from '@/config/navigation'
import { siteConfig } from '@/config/site'

export default function Footer() {
  return (
    <footer className="bg-[#111827] border-t border-[#374151] mt-auto">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-8">
          {/* Brand */}
          <div className="col-span-2 lg:col-span-1">
            <Link href="/" className="flex items-center gap-2 mb-4">
              <Zap className="h-6 w-6 text-[#22d3ee]" />
              <span className="text-lg font-bold bg-gradient-to-r from-[#3b82f6] to-[#22d3ee] bg-clip-text text-transparent">
                GeekendZone
              </span>
            </Link>
            <p className="text-sm text-gray-500 mb-4">{siteConfig.tagline}</p>
            <div className="flex gap-3">
              <a href={siteConfig.social.twitter} className="text-gray-500 hover:text-[#22d3ee] transition-colors">
                <Twitter className="h-4 w-4" />
              </a>
              <a href={siteConfig.social.github} className="text-gray-500 hover:text-[#22d3ee] transition-colors">
                <Github className="h-4 w-4" />
              </a>
              <a href={siteConfig.social.linkedin} className="text-gray-500 hover:text-[#22d3ee] transition-colors">
                <Linkedin className="h-4 w-4" />
              </a>
            </div>
          </div>

          {/* Shop */}
          <div>
            <h3 className="text-sm font-semibold text-white mb-4">Shop</h3>
            <ul className="space-y-2">
              {footerLinks.shop.map(link => (
                <li key={link.href + link.label}>
                  <Link href={link.href} className="text-sm text-gray-500 hover:text-white transition-colors">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Services */}
          <div>
            <h3 className="text-sm font-semibold text-white mb-4">Services</h3>
            <ul className="space-y-2">
              {footerLinks.services.map(link => (
                <li key={link.label}>
                  <Link href={link.href} className="text-sm text-gray-500 hover:text-white transition-colors">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Support */}
          <div>
            <h3 className="text-sm font-semibold text-white mb-4">Support</h3>
            <ul className="space-y-2">
              {footerLinks.support.map(link => (
                <li key={link.label}>
                  <Link href={link.href} className="text-sm text-gray-500 hover:text-white transition-colors">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Company */}
          <div>
            <h3 className="text-sm font-semibold text-white mb-4">Company</h3>
            <ul className="space-y-2">
              {footerLinks.company.map(link => (
                <li key={link.label}>
                  <Link href={link.href} className="text-sm text-gray-500 hover:text-white transition-colors">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
            <div className="mt-4 text-xs text-gray-600">
              <p>{siteConfig.contact.email}</p>
              <p>{siteConfig.contact.phone}</p>
            </div>
          </div>
        </div>

        <Separator className="my-8 bg-[#374151]" />

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-gray-600">
          <p>© {new Date().getFullYear()} GeekendZone. All rights reserved.</p>
          <div className="flex gap-4">
            <Link href="#" className="hover:text-gray-400 transition-colors">Privacy Policy</Link>
            <Link href="#" className="hover:text-gray-400 transition-colors">Terms of Service</Link>
            <Link href="#" className="hover:text-gray-400 transition-colors">Cookie Policy</Link>
          </div>
        </div>
      </div>
    </footer>
  )
}

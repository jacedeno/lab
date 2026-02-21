'use client'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { User, Mail, Phone, Edit2 } from 'lucide-react'

export default function ProfileCard() {
  // Mock user data
  const user = {
    name: 'Alex Thompson',
    email: 'alex@example.com',
    phone: '+1 (555) 123-4567',
    initials: 'AT',
  }

  return (
    <div className="bg-[#111827] border border-[#374151] rounded-xl p-6">
      {/* Avatar section */}
      <div className="flex items-center gap-4 mb-6">
        <Avatar className="h-16 w-16 border-2 border-[#3b82f6]">
          <AvatarImage src="" />
          <AvatarFallback className="bg-[#1f2937] text-[#22d3ee] text-lg font-bold">{user.initials}</AvatarFallback>
        </Avatar>
        <div>
          <h2 className="text-xl font-bold text-white">{user.name}</h2>
          <p className="text-sm text-gray-400">Customer since 2025</p>
        </div>
        <Button variant="outline" size="sm" className="ml-auto border-[#374151] text-gray-300 hover:bg-[#1f2937]">
          <Edit2 className="h-4 w-4 mr-2" />
          Edit
        </Button>
      </div>

      <Separator className="bg-[#374151] mb-6" />

      {/* Profile fields */}
      <div className="space-y-4">
        <div>
          <Label className="text-gray-400 text-sm flex items-center gap-1.5 mb-1.5">
            <User className="h-3.5 w-3.5" /> Full Name
          </Label>
          <Input defaultValue={user.name} className="bg-[#1f2937] border-[#374151] text-white" />
        </div>
        <div>
          <Label className="text-gray-400 text-sm flex items-center gap-1.5 mb-1.5">
            <Mail className="h-3.5 w-3.5" /> Email
          </Label>
          <Input defaultValue={user.email} type="email" className="bg-[#1f2937] border-[#374151] text-white" />
        </div>
        <div>
          <Label className="text-gray-400 text-sm flex items-center gap-1.5 mb-1.5">
            <Phone className="h-3.5 w-3.5" /> Phone
          </Label>
          <Input defaultValue={user.phone} type="tel" className="bg-[#1f2937] border-[#374151] text-white" />
        </div>
      </div>

      <div className="flex gap-3 mt-6">
        <Button className="bg-[#3b82f6] hover:bg-[#2563eb] text-white">Save Changes</Button>
        <Button variant="outline" className="border-[#374151] text-gray-300 hover:bg-[#1f2937]">Cancel</Button>
      </div>
    </div>
  )
}

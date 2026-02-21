import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import LoginForm from '@/components/account/LoginForm'
import RegisterForm from '@/components/account/RegisterForm'
import { Zap } from 'lucide-react'

export default function AccountPage() {
  return (
    <div className="w-full max-w-md">
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-2 mb-4">
          <Zap className="h-6 w-6 text-[#22d3ee]" />
          <span className="text-xl font-bold bg-gradient-to-r from-[#3b82f6] to-[#22d3ee] bg-clip-text text-transparent">GeekendZone</span>
        </div>
        <h1 className="text-2xl font-bold text-white">Welcome back</h1>
        <p className="text-gray-400 text-sm mt-1">Sign in to your account or create a new one</p>
      </div>

      <div className="bg-[#111827] border border-[#374151] rounded-2xl p-6">
        <Tabs defaultValue="login">
          <TabsList className="w-full bg-[#1f2937] border border-[#374151] mb-6">
            <TabsTrigger value="login" className="flex-1 data-[state=active]:bg-[#3b82f6] data-[state=active]:text-white text-gray-400">Sign In</TabsTrigger>
            <TabsTrigger value="register" className="flex-1 data-[state=active]:bg-[#3b82f6] data-[state=active]:text-white text-gray-400">Create Account</TabsTrigger>
          </TabsList>
          <TabsContent value="login"><LoginForm /></TabsContent>
          <TabsContent value="register"><RegisterForm /></TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

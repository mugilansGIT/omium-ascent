"use client"
import { useState } from "react"
import { Settings, Bell, Shield, User } from "lucide-react"
import { createClient } from "@/lib/supabase/client"

export default function SettingsPage() {
  const supabase = createClient()
  const [password, setPassword] = useState("")
  const [saving, setSaving] = useState(false)
  const [msg, setMsg] = useState("")

  const handlePasswordChange = async () => {
    setSaving(true)
    const { error } = await supabase.auth.updateUser({ password })
    setMsg(error ? error.message : "Password updated successfully!")
    setSaving(false)
    setPassword("")
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-500 mt-1">Manage your account and preferences</p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
        <div className="flex items-center gap-2 mb-2">
          <User className="h-5 w-5 text-blue-500" />
          <h2 className="font-semibold">Security</h2>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">New Password</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)}
            className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="Enter new password" />
        </div>
        {msg && <p className={`text-sm ${msg.includes("success") ? "text-green-600" : "text-red-600"}`}>{msg}</p>}
        <button onClick={handlePasswordChange} disabled={!password || saving}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
          {saving ? "Saving..." : "Update Password"}
        </button>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Bell className="h-5 w-5 text-blue-500" />
          <h2 className="font-semibold">Notifications</h2>
        </div>
        <div className="space-y-3">
          {["Leave request updates", "Task assignments", "Meeting reminders", "Procurement status"].map(item => (
            <div key={item} className="flex items-center justify-between">
              <span className="text-sm text-gray-700">{item}</span>
              <button className="relative inline-flex h-5 w-9 items-center rounded-full bg-blue-600 transition-colors">
                <span className="inline-block h-3 w-3 transform rounded-full bg-white translate-x-5 transition-transform" />
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-blue-50 rounded-xl border border-blue-100 p-4">
        <div className="flex items-center gap-2 mb-2">
          <Shield className="h-4 w-4 text-blue-600" />
          <p className="text-sm font-medium text-blue-800">API Configuration</p>
        </div>
        <p className="text-sm text-blue-700">Backend URL: <code className="bg-blue-100 px-1 rounded">{process.env.NEXT_PUBLIC_API_URL || "Not configured"}</code></p>
      </div>
    </div>
  )
}

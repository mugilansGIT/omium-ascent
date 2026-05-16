"use client"
import { useEffect, useState } from "react"
import { Calendar, Plus, X } from "lucide-react"
import { api } from "@/lib/api"

const statusColors: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-700",
  ai_approved: "bg-green-100 text-green-700",
  approved: "bg-green-100 text-green-700",
  rejected: "bg-red-100 text-red-700",
  escalated: "bg-orange-100 text-orange-700",
}

export default function LeavesPage() {
  const [leaves, setLeaves] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [form, setForm] = useState({ start_date: "", end_date: "", reason: "", policy_id: "annual" })

  useEffect(() => {
    const fetchLeaves = () => {
      api.get("/leaves")
        .then(r => { setLeaves(r.data || []); setLoading(false) })
        .catch(() => setLoading(false))
    }
    
    fetchLeaves() // Initial fetch
    const intervalId = setInterval(fetchLeaves, 5000) // Poll every 5 seconds
    
    return () => clearInterval(intervalId) // Cleanup on unmount
  }, [])

  const handleSubmit = async () => {
    if (!form.start_date || !form.end_date) return
    setSubmitting(true)
    try {
      const start = new Date(form.start_date)
      const end = new Date(form.end_date)
      const days = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1
      const res = await api.post("/leaves/request", { ...form, total_days: days })
      setResult(res.data)
      setLeaves(prev => [res.data, ...prev])
      setShowForm(false)
      setForm({ start_date: "", end_date: "", reason: "", policy_id: "annual" })
    } catch (e: any) {
      setResult({ error: e.response?.data?.detail || "Failed to submit" })
    }
    setSubmitting(false)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Leave Management</h1>
          <p className="text-gray-500 mt-1">AI-powered leave processing</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm font-medium"
        >
          <Plus className="h-4 w-4" /> Request Leave
        </button>
      </div>

      {result && (
        <div className={`p-4 rounded-xl border ${result.error ? "bg-red-50 border-red-200 text-red-700" : "bg-green-50 border-green-200 text-green-700"}`}>
          {result.error ? result.error : `Leave request submitted! Status: ${result.status}. ${result.message || ""}`}
        </div>
      )}

      {/* Leave Request Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl w-full max-w-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-bold text-lg">Request Leave</h2>
              <button onClick={() => setShowForm(false)}><X className="h-5 w-5 text-gray-400" /></button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                <input type="date" value={form.start_date} onChange={e => setForm(p => ({ ...p, start_date: e.target.value }))}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                <input type="date" value={form.end_date} onChange={e => setForm(p => ({ ...p, end_date: e.target.value }))}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Reason</label>
                <textarea value={form.reason} onChange={e => setForm(p => ({ ...p, reason: e.target.value }))}
                  rows={3} placeholder="Reason for leave..."
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none" />
              </div>
              <button onClick={handleSubmit} disabled={submitting}
                className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium text-sm">
                {submitting ? "AI Processing..." : "Submit Request"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Leave list */}
      <div className="bg-white rounded-xl border border-gray-200">
        {loading ? (
          <div className="p-8 text-center text-gray-400">Loading...</div>
        ) : leaves.length === 0 ? (
          <div className="p-8 text-center text-gray-400">
            <Calendar className="h-10 w-10 mx-auto mb-2 opacity-30" />
            <p>No leave requests yet</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {leaves.map(leave => (
              <div key={leave.id} className="p-4 flex items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm text-gray-900">
                      {leave.start_date} → {leave.end_date}
                    </span>
                    <span className="text-xs text-gray-500">({leave.total_days} days)</span>
                  </div>
                  {leave.reason && <p className="text-sm text-gray-500 mt-0.5">{leave.reason}</p>}
                  {leave.ai_decision?.reason && (
                    <p className="text-xs text-gray-400 mt-1 italic">AI: {leave.ai_decision.reason}</p>
                  )}
                </div>
                <span className={`text-xs px-2 py-1 rounded-full font-medium whitespace-nowrap ${statusColors[leave.status] || "bg-gray-100 text-gray-600"}`}>
                  {leave.status?.replace("_", " ")}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

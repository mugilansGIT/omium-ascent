"use client"
import { useEffect, useState } from "react"
import { ShoppingCart, Plus, X, CheckCircle, Clock } from "lucide-react"
import { api } from "@/lib/api"

const statusColors: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-700",
  ai_processing: "bg-blue-100 text-blue-700",
  ai_processed: "bg-purple-100 text-purple-700",
  approved: "bg-green-100 text-green-700",
  ordered: "bg-indigo-100 text-indigo-700",
  received: "bg-gray-100 text-gray-600",
}

export default function ProcurementPage() {
  const [requests, setRequests] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [form, setForm] = useState({ product_name: "", description: "", quantity: 1, estimated_budget: "", urgency: "normal" })

  useEffect(() => {
    api.get("/procurement").then(r => { setRequests(r.data || []); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  const handleSubmit = async () => {
    setSubmitting(true)
    try {
      const res = await api.post("/procurement/request", form)
      setRequests(prev => [res.data, ...prev])
      setShowForm(false)
      setForm({ product_name: "", description: "", quantity: 1, estimated_budget: "", urgency: "normal" })
    } catch (e) { alert("Failed to submit request") }
    setSubmitting(false)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Procurement</h1>
          <p className="text-gray-500 mt-1">AI-powered vendor selection and PO generation</p>
        </div>
        <button onClick={() => setShowForm(true)} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm font-medium">
          <Plus className="h-4 w-4" /> New Request
        </button>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl w-full max-w-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-bold text-lg">New Procurement Request</h2>
              <button onClick={() => setShowForm(false)}><X className="h-5 w-5 text-gray-400" /></button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Product Name</label>
                <input value={form.product_name} onChange={e => setForm(p => ({ ...p, product_name: e.target.value }))}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="e.g. Office Laptops" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea value={form.description} onChange={e => setForm(p => ({ ...p, description: e.target.value }))}
                  rows={2} className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none" placeholder="Specifications..." />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Quantity</label>
                  <input type="number" value={form.quantity} onChange={e => setForm(p => ({ ...p, quantity: Number(e.target.value) }))}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" min={1} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Budget (₹)</label>
                  <input type="number" value={form.estimated_budget} onChange={e => setForm(p => ({ ...p, estimated_budget: e.target.value }))}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="0" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Urgency</label>
                <select value={form.urgency} onChange={e => setForm(p => ({ ...p, urgency: e.target.value }))}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option value="low">Low</option>
                  <option value="normal">Normal</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
              <button onClick={handleSubmit} disabled={submitting}
                className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium text-sm">
                {submitting ? "Submitting to AI..." : "Submit Request"}
              </button>
            </div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="p-8 text-center text-gray-400">Loading...</div>
      ) : requests.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400">
          <ShoppingCart className="h-10 w-10 mx-auto mb-2 opacity-30" />
          <p>No procurement requests</p>
        </div>
      ) : (
        <div className="space-y-4">
          {requests.map(req => (
            <div key={req.id} className="bg-white rounded-xl border border-gray-200 p-5">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="font-semibold text-gray-900">{req.product_name}</h3>
                    <span className="text-xs text-gray-500">Qty: {req.quantity}</span>
                    {req.estimated_budget && <span className="text-xs text-gray-500">Budget: ₹{Number(req.estimated_budget).toLocaleString()}</span>}
                  </div>
                  {req.description && <p className="text-sm text-gray-500 mt-1">{req.description}</p>}
                  {req.ai_recommendation?.recommendation_summary && (
                    <div className="mt-3 p-3 bg-purple-50 rounded-lg">
                      <p className="text-xs font-medium text-purple-700 mb-1">AI Recommendation</p>
                      <p className="text-sm text-purple-800">{req.ai_recommendation.recommendation_summary}</p>
                    </div>
                  )}
                </div>
                <span className={`text-xs px-2 py-1 rounded-full font-medium whitespace-nowrap ${statusColors[req.status] || "bg-gray-100 text-gray-600"}`}>
                  {req.status?.replace("_", " ")}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

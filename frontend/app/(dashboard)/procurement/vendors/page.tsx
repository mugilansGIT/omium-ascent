"use client"
import { useEffect, useState } from "react"
import { Building2, Star, Search } from "lucide-react"
import { api } from "@/lib/api"

export default function VendorsPage() {
  const [vendors, setVendors] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")

  useEffect(() => {
    api.get("/vendors").then(r => { setVendors(r.data || []); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  const filtered = vendors.filter(v =>
    v.name?.toLowerCase().includes(search.toLowerCase()) ||
    v.category?.toLowerCase().includes(search.toLowerCase())
  )

  const scoreBar = (score: number) => (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-gray-100 rounded-full h-1.5">
        <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: `${(score || 0) * 100}%` }} />
      </div>
      <span className="text-xs text-gray-500">{((score || 0) * 100).toFixed(0)}%</span>
    </div>
  )

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Vendors</h1>
        <p className="text-gray-500 mt-1">AI-scored vendor intelligence</p>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search vendors..."
          className="w-full pl-9 pr-4 py-2 border border-gray-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>

      {loading ? (
        <div className="p-8 text-center text-gray-400">Loading...</div>
      ) : filtered.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400">
          <Building2 className="h-10 w-10 mx-auto mb-2 opacity-30" />
          <p>No vendors found</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map(vendor => (
            <div key={vendor.id} className="bg-white rounded-xl border border-gray-200 p-5 hover:border-blue-200 transition-colors">
              <div className="flex items-start justify-between gap-2 mb-3">
                <div>
                  <h3 className="font-semibold text-gray-900">{vendor.name}</h3>
                  <p className="text-xs text-gray-500 mt-0.5">{vendor.category} • {vendor.country}</p>
                </div>
                {vendor.verified && (
                  <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">Verified</span>
                )}
              </div>
              <div className="space-y-2">
                <div>
                  <p className="text-xs text-gray-500 mb-1">Reliability</p>
                  {scoreBar(vendor.reliability_score)}
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-1">Quality</p>
                  {scoreBar(vendor.quality_score)}
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-1">Price Competitiveness</p>
                  {scoreBar(vendor.price_competitiveness)}
                </div>
              </div>
              {vendor.email && (
                <p className="text-xs text-blue-600 mt-3 truncate">{vendor.email}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

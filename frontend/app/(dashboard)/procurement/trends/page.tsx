"use client"
import { useEffect, useState } from "react"
import { TrendingUp, RefreshCw } from "lucide-react"
import { api } from "@/lib/api"

export default function TrendsPage() {
  const [trends, setTrends] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [scanning, setScanning] = useState(false)

  const fetchTrends = () => {
    setLoading(true)
    api.get("/trends").then(r => { setTrends(r.data || []); setLoading(false) }).catch(() => setLoading(false))
  }

  useEffect(() => { fetchTrends() }, [])

  const triggerScan = async () => {
    setScanning(true)
    try { await api.post("/trends/scan") } catch (e) {}
    setTimeout(() => { setScanning(false); fetchTrends() }, 3000)
  }

  const longevityColor: Record<string, string> = {
    short_term: "bg-red-100 text-red-700",
    medium_term: "bg-yellow-100 text-yellow-700",
    long_term: "bg-green-100 text-green-700",
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Trend Intelligence</h1>
          <p className="text-gray-500 mt-1">AI-identified market trends</p>
        </div>
        <button onClick={triggerScan} disabled={scanning}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm font-medium disabled:opacity-50">
          <RefreshCw className={`h-4 w-4 ${scanning ? "animate-spin" : ""}`} />
          {scanning ? "Scanning..." : "Trigger Scan"}
        </button>
      </div>

      {loading ? (
        <div className="p-8 text-center text-gray-400">Loading...</div>
      ) : trends.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400">
          <TrendingUp className="h-10 w-10 mx-auto mb-2 opacity-30" />
          <p>No trends identified yet. Trigger a scan!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {trends.map(trend => (
            <div key={trend.id} className="bg-white rounded-xl border border-gray-200 p-5">
              <div className="flex items-start justify-between gap-2 mb-3">
                <h3 className="font-semibold text-gray-900">{trend.product_name}</h3>
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${longevityColor[trend.longevity_estimate] || "bg-gray-100 text-gray-600"}`}>
                  {trend.longevity_estimate?.replace("_", " ")}
                </span>
              </div>
              <p className="text-xs text-gray-500 mb-3">{trend.category}</p>

              <div className="space-y-2">
                <div>
                  <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>Trend Score</span>
                    <span>{((trend.trend_score || 0) * 100).toFixed(0)}%</span>
                  </div>
                  <div className="bg-gray-100 rounded-full h-1.5">
                    <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: `${(trend.trend_score || 0) * 100}%` }} />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>Sustainability</span>
                    <span>{((trend.sustainability_score || 0) * 100).toFixed(0)}%</span>
                  </div>
                  <div className="bg-gray-100 rounded-full h-1.5">
                    <div className="bg-green-500 h-1.5 rounded-full" style={{ width: `${(trend.sustainability_score || 0) * 100}%` }} />
                  </div>
                </div>
              </div>

              {trend.ai_analysis && (
                <p className="text-xs text-gray-500 mt-3 line-clamp-3">{trend.ai_analysis}</p>
              )}
              <p className="text-xs text-gray-300 mt-2">{trend.identified_at ? new Date(trend.identified_at).toLocaleDateString() : ""}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

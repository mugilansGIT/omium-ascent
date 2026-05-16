"use client"
import { useEffect, useState } from "react"

export function AgentStatusPanel() {
  const [status, setStatus] = useState<Record<string, boolean>>({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const poll = async () => {
      try {
        const r = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/health`)
        const data = await r.json()
        setStatus(data.agents || {})
      } catch {
        setStatus({})
      }
      setLoading(false)
    }
    poll()
    const interval = setInterval(poll, 5000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="p-4 space-y-2">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="h-8 bg-gray-100 rounded animate-pulse" />
        ))}
      </div>
    )
  }

  if (Object.keys(status).length === 0) {
    return (
      <div className="p-4 text-center text-sm text-gray-400">
        Backend not reachable
      </div>
    )
  }

  return (
    <div className="p-4 space-y-2">
      {Object.entries(status).map(([name, running]) => (
        <div key={name} className="flex items-center gap-2 text-sm">
          <span className={`w-2 h-2 rounded-full flex-shrink-0 ${running ? "bg-green-500" : "bg-red-400"}`} />
          <span className="flex-1 capitalize text-gray-700">{name.replace(/_/g, " ")}</span>
          <span className={`text-xs font-medium ${running ? "text-green-600" : "text-red-500"}`}>
            {running ? "Running" : "Stopped"}
          </span>
        </div>
      ))}
    </div>
  )
}

"use client"
import { useEffect, useState } from "react"
import { api } from "@/lib/api"

interface AgentEvent {
  id: string
  agent_name: string
  event_type: string
  status: string
  created_at: string
  processing_time_ms?: number
}

export function ActivityFeed() {
  const [events, setEvents] = useState<AgentEvent[]>([])
  const [loading, setLoading] = useState(true)

  const fetchEvents = () => {
    api.get("/reports/agent-events?limit=20")
      .then(r => { setEvents(r.data || []); setLoading(false) })
      .catch(() => setLoading(false))
  }

  useEffect(() => {
    fetchEvents()
    const interval = setInterval(fetchEvents, 5000) // Poll every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const getEventDescription = (event: AgentEvent) => {
    const type = event.event_type
    if (type === "hr:leave:requested") return "HR: New leave request received"
    if (type === "hr:leave:approved") return "HR: Leave request approved by AI"
    if (type === "hr:leave:rejected") return "HR: Leave request rejected by AI"
    if (type === "task:overdue") return "Task: System detected overdue task"
    if (type === "meeting:transcript_ready") return "Meeting: New transcript being processed"
    if (type === "procurement:requested") return "Procurement: Analyzing new request"
    if (type === "procurement:vendor_analyzed") return "Procurement: Vendor analysis complete"
    return type
  }

  const statusColor: Record<string, string> = {
    success: "bg-green-100 text-green-700",
    failed: "bg-red-100 text-red-700",
    processing: "bg-yellow-100 text-yellow-700",
    pending: "bg-gray-100 text-gray-600",
  }

  if (loading) {
    return (
      <div className="p-4 space-y-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-12 bg-gray-100 rounded animate-pulse" />
        ))}
      </div>
    )
  }

  if (events.length === 0) {
    return (
      <div className="p-12 text-center">
        <p className="text-sm text-gray-400">No recent agent activity</p>
        <p className="text-xs text-gray-300 mt-1 italic">Waiting for agents to report...</p>
      </div>
    )
  }

  return (
    <div className="divide-y divide-gray-100 max-h-96 overflow-y-auto">
      {events.map(event => (
        <div key={event.id} className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors">
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-gray-900 truncate">
              {getEventDescription(event)}
            </p>
            <p className="text-xs text-gray-500 mt-0.5">
              <span className="capitalize">{event.agent_name.replace("_", " ")}</span> • {new Date(event.created_at).toLocaleTimeString()}
            </p>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            {event.processing_time_ms && (
              <span className="text-[10px] text-gray-400 font-mono">{event.processing_time_ms}ms</span>
            )}
            <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${statusColor[event.status] || statusColor.pending}`}>
              {event.status}
            </span>
          </div>
        </div>
      ))}
    </div>
  )
}

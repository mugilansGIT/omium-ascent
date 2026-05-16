"use client"
import { useEffect, useState } from "react"
import { FileText, Clock, Plus, Users } from "lucide-react"
import { api } from "@/lib/api"

export default function MeetingsPage() {
  const [meetings, setMeetings] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get("/meetings").then(r => { setMeetings(r.data || []); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Meetings</h1>
          <p className="text-gray-500 mt-1">AI-summarized meeting records</p>
        </div>
        <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm font-medium">
          <Plus className="h-4 w-4" /> Schedule Meeting
        </button>
      </div>

      {loading ? (
        <div className="p-8 text-center text-gray-400">Loading...</div>
      ) : meetings.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400">
          <FileText className="h-10 w-10 mx-auto mb-2 opacity-30" />
          <p>No meetings scheduled</p>
        </div>
      ) : (
        <div className="space-y-4">
          {meetings.map(meeting => (
            <div key={meeting.id} className="bg-white rounded-xl border border-gray-200 p-5">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">{meeting.title}</h3>
                  <div className="flex items-center gap-4 mt-2 text-sm text-gray-500 flex-wrap">
                    <span className="flex items-center gap-1">
                      <Clock className="h-3.5 w-3.5" />
                      {meeting.scheduled_at ? new Date(meeting.scheduled_at).toLocaleString() : "—"}
                    </span>
                    <span>{meeting.duration_minutes} min</span>
                    <span className="capitalize">{meeting.meeting_type}</span>
                  </div>
                  {meeting.ai_summary && (
                    <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                      <p className="text-xs font-medium text-blue-700 mb-1">AI Summary</p>
                      <p className="text-sm text-blue-800">{meeting.ai_summary}</p>
                    </div>
                  )}
                  {meeting.action_items && Array.isArray(meeting.action_items) && meeting.action_items.length > 0 && (
                    <div className="mt-2">
                      <p className="text-xs font-medium text-gray-500 mb-1">Action Items ({meeting.action_items.length})</p>
                      <ul className="text-sm text-gray-600 space-y-1">
                        {meeting.action_items.slice(0, 3).map((item: any, i: number) => (
                          <li key={i} className="flex items-center gap-2">
                            <span className="w-1.5 h-1.5 bg-blue-400 rounded-full" />
                            {typeof item === "string" ? item : item.description}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
                <span className={`text-xs px-2 py-1 rounded-full font-medium whitespace-nowrap ${meeting.status === "completed" ? "bg-green-100 text-green-700" : meeting.status === "cancelled" ? "bg-red-100 text-red-700" : "bg-blue-100 text-blue-700"}`}>
                  {meeting.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

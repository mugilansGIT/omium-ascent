"use client"
import { useEffect, useState } from "react"
import { Users, CheckSquare, Calendar, ShoppingCart, TrendingUp, AlertCircle } from "lucide-react"
import { AgentStatusPanel } from "@/components/agents/AgentStatusPanel"
import { StatsCard } from "@/components/shared/StatsCard"
import { ActivityFeed } from "@/components/shared/ActivityFeed"
import { api } from "@/lib/api"

export default function DashboardPage() {
  const [stats, setStats] = useState({
    employees: 0, tasks: 0, pendingLeaves: 0, openProcurements: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [emps, tasks, leaves] = await Promise.allSettled([
          api.get("/employees"),
          api.get("/tasks"),
          api.get("/leaves?status=pending"),
        ])
        setStats({
          employees: emps.status === "fulfilled" ? (emps.value.data?.length || 0) : 0,
          tasks: tasks.status === "fulfilled" ? (tasks.value.data?.length || 0) : 0,
          pendingLeaves: leaves.status === "fulfilled" ? (leaves.value.data?.length || 0) : 0,
          openProcurements: 0
        })
      } catch (e) {}
      setLoading(false)
    }
    fetchStats()
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 mt-1">AI-powered operations overview</p>
        </div>
        <a href="/leaves" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm font-medium transition-colors">
          + Request Leave
        </a>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatsCard title="Total Employees" value={stats.employees} icon={Users} color="blue" loading={loading} />
        <StatsCard title="Active Tasks" value={stats.tasks} icon={CheckSquare} color="green" loading={loading} />
        <StatsCard title="Pending Leaves" value={stats.pendingLeaves} icon={Calendar} color="yellow" loading={loading} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Agent Status */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div className="px-4 py-3 border-b border-gray-200 flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-blue-500" />
              <h2 className="font-semibold text-gray-800">Agent Status</h2>
            </div>
            <AgentStatusPanel />
          </div>
        </div>

        {/* Activity Feed */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div className="px-4 py-3 border-b border-gray-200 flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-orange-500" />
              <h2 className="font-semibold text-gray-800">Recent Activity</h2>
            </div>
            <ActivityFeed />
          </div>
        </div>
      </div>
    </div>
  )
}

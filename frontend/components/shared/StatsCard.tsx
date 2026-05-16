import { LucideIcon } from "lucide-react"

const colorMap: Record<string, { bg: string; text: string; icon: string }> = {
  blue:   { bg: "bg-blue-50",   text: "text-blue-700",   icon: "text-blue-500" },
  green:  { bg: "bg-green-50",  text: "text-green-700",  icon: "text-green-500" },
  yellow: { bg: "bg-yellow-50", text: "text-yellow-700", icon: "text-yellow-500" },
  purple: { bg: "bg-purple-50", text: "text-purple-700", icon: "text-purple-500" },
  red:    { bg: "bg-red-50",    text: "text-red-700",    icon: "text-red-500" },
}

interface StatsCardProps {
  title: string
  value: number | string
  icon: LucideIcon
  color?: string
  loading?: boolean
}

export function StatsCard({ title, value, icon: Icon, color = "blue", loading }: StatsCardProps) {
  const c = colorMap[color] || colorMap.blue

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-500 font-medium">{title}</p>
        <div className={`w-9 h-9 ${c.bg} rounded-lg flex items-center justify-center`}>
          <Icon className={`h-5 w-5 ${c.icon}`} />
        </div>
      </div>
      {loading ? (
        <div className="h-8 w-16 bg-gray-100 rounded animate-pulse mt-3" />
      ) : (
        <p className={`text-3xl font-bold mt-3 ${c.text}`}>{value}</p>
      )}
    </div>
  )
}

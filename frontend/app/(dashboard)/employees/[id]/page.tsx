"use client"
import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { ArrowLeft, Mail, Phone, Calendar, Building2 } from "lucide-react"
import { api } from "@/lib/api"

export default function EmployeeDetailPage() {
  const { id } = useParams()
  const [employee, setEmployee] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get(`/employees/${id}`).then(r => { setEmployee(r.data); setLoading(false) }).catch(() => setLoading(false))
  }, [id])

  if (loading) return <div className="p-8 text-center text-gray-400">Loading...</div>
  if (!employee) return <div className="p-8 text-center text-gray-400">Employee not found</div>

  return (
    <div className="space-y-6">
      <Link href="/dashboard/employees" className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
        <ArrowLeft className="h-4 w-4" /> Back to Employees
      </Link>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center gap-5">
          <div className="w-16 h-16 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-2xl font-bold">
            {employee.full_name?.[0] || "?"}
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{employee.full_name}</h1>
            <p className="text-gray-500">{employee.designation || employee.role}</p>
            <span className={`text-xs px-2 py-1 rounded-full font-medium ${employee.status === "active" ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-600"}`}>
              {employee.status}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6">
          <div className="flex items-center gap-3 text-sm text-gray-600">
            <Mail className="h-4 w-4 text-gray-400" />{employee.email}
          </div>
          {employee.phone && (
            <div className="flex items-center gap-3 text-sm text-gray-600">
              <Phone className="h-4 w-4 text-gray-400" />{employee.phone}
            </div>
          )}
          <div className="flex items-center gap-3 text-sm text-gray-600">
            <Calendar className="h-4 w-4 text-gray-400" />Joined {employee.join_date ? new Date(employee.join_date).toLocaleDateString() : "—"}
          </div>
          <div className="flex items-center gap-3 text-sm text-gray-600">
            <Building2 className="h-4 w-4 text-gray-400" />{employee.departments?.name || "No department"}
          </div>
        </div>
      </div>
    </div>
  )
}

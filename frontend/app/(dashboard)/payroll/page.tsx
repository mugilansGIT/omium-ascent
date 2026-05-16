"use client"
import { useEffect, useState } from "react"
import { DollarSign } from "lucide-react"
import { api } from "@/lib/api"

export default function PayrollPage() {
  const [records, setRecords] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get("/payroll").then(r => { setRecords(r.data || []); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Payroll</h1>
        <p className="text-gray-500 mt-1">Salary records and disbursements</p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200">
        {loading ? (
          <div className="p-8 text-center text-gray-400">Loading...</div>
        ) : records.length === 0 ? (
          <div className="p-8 text-center text-gray-400">
            <DollarSign className="h-10 w-10 mx-auto mb-2 opacity-30" />
            <p>No payroll records</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 text-left">
                <tr>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Period</th>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Employee</th>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Base</th>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Net Salary</th>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {records.map(r => (
                  <tr key={r.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-600">{r.payroll_periods?.period_name || "—"}</td>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{r.employees?.full_name || "—"}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">₹{r.base_salary?.toLocaleString()}</td>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">₹{r.net_salary?.toLocaleString()}</td>
                    <td className="px-4 py-3">
                      <span className={`text-xs px-2 py-1 rounded-full font-medium ${r.status === "paid" ? "bg-green-100 text-green-700" : r.status === "approved" ? "bg-blue-100 text-blue-700" : "bg-gray-100 text-gray-600"}`}>
                        {r.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

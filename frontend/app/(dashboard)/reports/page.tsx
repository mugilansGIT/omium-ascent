"use client"
import { FileText, Download } from "lucide-react"
import { api } from "@/lib/api"

const reportTypes = [
  { id: "employee_summary", label: "Employee Summary", desc: "Overview of all employees, departments, and roles" },
  { id: "attendance_report", label: "Attendance Report", desc: "Monthly attendance and hours worked" },
  { id: "leave_report", label: "Leave Report", desc: "Leave requests, approvals, and balances" },
  { id: "payroll_report", label: "Payroll Report", desc: "Salary disbursements and deductions" },
  { id: "task_performance", label: "Task Performance", desc: "Task completion rates and overdue tasks" },
  { id: "procurement_report", label: "Procurement Report", desc: "Purchase orders and vendor performance" },
]

export default function ReportsPage() {
  const handleGenerate = async (reportId: string) => {
    try {
      const res = await api.get(`/reports/${reportId}`, { responseType: "blob" })
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement("a")
      link.href = url
      link.download = `${reportId}_${new Date().toISOString().slice(0, 10)}.pdf`
      link.click()
    } catch (e) {
      alert("Report generation failed. Please check backend.")
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
        <p className="text-gray-500 mt-1">Generate AI-powered business reports</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {reportTypes.map(report => (
          <div key={report.id} className="bg-white rounded-xl border border-gray-200 p-5 hover:border-blue-200 transition-colors">
            <FileText className="h-8 w-8 text-blue-500 mb-3" />
            <h3 className="font-semibold text-gray-900 mb-1">{report.label}</h3>
            <p className="text-sm text-gray-500 mb-4">{report.desc}</p>
            <button
              onClick={() => handleGenerate(report.id)}
              className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              <Download className="h-4 w-4" /> Generate PDF
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

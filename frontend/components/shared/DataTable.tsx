interface Column<T> {
  key: keyof T | string
  label: string
  render?: (value: any, row: T) => React.ReactNode
}

interface DataTableProps<T> {
  columns: Column<T>[]
  data: T[]
  loading?: boolean
  emptyMessage?: string
}

export function DataTable<T extends { id: string }>({ columns, data, loading, emptyMessage }: DataTableProps<T>) {
  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="p-8 text-center text-gray-400">Loading...</div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      {data.length === 0 ? (
        <div className="p-8 text-center text-gray-400">{emptyMessage || "No data"}</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 text-left">
              <tr>
                {columns.map(col => (
                  <th key={String(col.key)} className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">
                    {col.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {data.map(row => (
                <tr key={row.id} className="hover:bg-gray-50">
                  {columns.map(col => {
                    const value = (row as any)[col.key as string]
                    return (
                      <td key={String(col.key)} className="px-4 py-3 text-sm text-gray-700">
                        {col.render ? col.render(value, row) : String(value ?? "—")}
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

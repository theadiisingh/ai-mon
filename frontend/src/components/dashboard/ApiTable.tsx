import { Link } from 'react-router-dom'
import { ApiEndpoint } from '../../types/api'
import StatusBadge from './StatusBadge'
import { formatPercentage, formatDuration, formatDateTime } from '../../utils/formatters'
import { Search } from 'lucide-react'

interface ApiTableProps {
  apis: ApiEndpoint[]
}

export default function ApiTable({ apis }: ApiTableProps) {
  if (apis.length === 0) {
    return (
      <div className="card p-12 text-center flex flex-col items-center justify-center border-dashed border-2 bg-zinc-50/50">
        <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-sm mb-4 border border-zinc-100">
          <Search className="h-6 w-6 text-zinc-400" />
        </div>
        <h3 className="text-lg font-semibold text-zinc-900 tracking-tight">No APIs registered</h3>
        <p className="mt-2 text-sm text-zinc-500 max-w-sm">Get started by adding a new API endpoint to begin monitoring downtime and performance.</p>
        <div className="mt-6">
          <Link to="/apis/new" className="btn btn-primary shadow-sm hover:shadow-floating">
            Add New API
          </Link>
        </div>
      </div>
    )
  }

  const getMethodStyle = (method: string) => {
    switch (method) {
      case 'GET': return 'bg-blue-50 text-blue-600 ring-1 ring-blue-500/20'
      case 'POST': return 'bg-emerald-50 text-emerald-600 ring-1 ring-emerald-500/20'
      case 'PUT': return 'bg-amber-50 text-amber-600 ring-1 ring-amber-500/20'
      case 'DELETE': return 'bg-rose-50 text-rose-600 ring-1 ring-rose-500/20'
      default: return 'bg-zinc-50 text-zinc-600 ring-1 ring-zinc-500/20'
    }
  }

  return (
    <div className="card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-zinc-200/80">
          <thead className="bg-zinc-50/80">
            <tr>
              <th className="px-6 py-3.5 text-left text-xs font-semibold text-zinc-500 uppercase tracking-wider">Name</th>
              <th className="px-6 py-3.5 text-left text-xs font-semibold text-zinc-500 uppercase tracking-wider">Method</th>
              <th className="px-6 py-3.5 text-left text-xs font-semibold text-zinc-500 uppercase tracking-wider">URL</th>
              <th className="px-6 py-3.5 text-left text-xs font-semibold text-zinc-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3.5 text-left text-xs font-semibold text-zinc-500 uppercase tracking-wider">Uptime</th>
              <th className="px-6 py-3.5 text-left text-xs font-semibold text-zinc-500 uppercase tracking-wider">Avg Response</th>
              <th className="px-6 py-3.5 text-left text-xs font-semibold text-zinc-500 uppercase tracking-wider">Last Check</th>
              <th className="px-6 py-3.5 text-right text-xs font-semibold text-zinc-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-zinc-100">
            {apis.map((api) => (
              <tr key={api.id} className="hover:bg-zinc-50/80 transition-colors group">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-semibold text-zinc-900">{api.name}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2.5 py-1 rounded-md text-[11px] font-bold tracking-wider ${getMethodStyle(api.method)}`}>
                    {api.method}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-zinc-500 truncate max-w-xs font-mono bg-zinc-50 px-2 py-1 rounded border border-zinc-100">{api.url}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <StatusBadge status={api.is_active ? 'active' : 'inactive'} />
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`text-sm font-semibold ${api.uptime_percentage >= 99 ? 'text-success-600' :
                      api.uptime_percentage >= 95 ? 'text-warning-600' :
                        'text-danger-600'
                    }`}>
                    {formatPercentage(api.uptime_percentage)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-zinc-500 font-medium">
                  {api.avg_response_time ? formatDuration(api.avg_response_time) : '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-zinc-500">
                  {api.updated_at ? formatDateTime(api.updated_at) : '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <Link to={`/apis/${api.id}`} className="text-primary-600 hover:text-primary-800 transition-colors bg-primary-50 px-3 py-1.5 rounded-md opacity-0 group-hover:opacity-100 focus:opacity-100">
                    View Details
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

import { Link } from 'react-router-dom'
import { ApiEndpoint } from '../../types/api'
import StatusBadge from './StatusBadge'
import { formatPercentage, formatDuration, formatDateTime } from '../../utils/formatters'
import { Search } from 'lucide-react'
import { motion } from 'framer-motion'

interface ApiTableProps {
  apis: ApiEndpoint[]
}

export default function ApiTable({ apis }: ApiTableProps) {
  if (apis.length === 0) {
    return (
      <motion.div 
        initial={{ opacity: 0, y: 4 }}
        animate={{ opacity: 1, y: 0 }}
        className="card p-10 text-center flex flex-col items-center justify-center border-dashed"
      >
        <div className="w-10 h-10 bg-surface-700/20 backdrop-blur-sm rounded-full flex items-center justify-center mb-4 border border-white/5">
          <Search className="h-4 w-4 text-content-tertiary" />
        </div>
        <h3 className="text-sm font-medium text-content-primary">No endpoints registered</h3>
        <p className="mt-1.5 text-xs text-content-tertiary max-w-xs">Add your first API endpoint to begin monitoring.</p>
        <div className="mt-5">
          <Link to="/apis/new" className="btn btn-primary text-xs">
            Add Endpoint
          </Link>
        </div>
      </motion.div>
    )
  }

  const getMethodStyle = (method: string) => {
    const baseStyle = 'bg-surface-700/20 backdrop-blur-sm border border-white/5'
    const methodColors: Record<string, string> = {
      GET: 'text-surface-300',
      POST: 'text-primary',
      PUT: 'text-warning',
      DELETE: 'text-danger',
      PATCH: 'text-accent',
    }
    return `${baseStyle} ${methodColors[method] || 'text-surface-400'}`
  }

  return (
    <div className="card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-white/5">
          <thead className="bg-surface-800/20 backdrop-blur-sm">
            <tr>
              <th className="table-header">Endpoint</th>
              <th className="table-header">Method</th>
              <th className="table-header">URL</th>
              <th className="table-header">Status</th>
              <th className="table-header">Uptime</th>
              <th className="table-header">Avg Response</th>
              <th className="table-header">Last Check</th>
              <th className="table-header text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 bg-surface-800/10">
            {apis.map((api, index) => (
              <motion.tr 
                key={api.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: index * 0.02 }}
                className="hover:bg-white/5 transition-colors duration-140"
              >
                <td className="table-cell whitespace-nowrap">
                  <div className="text-sm font-medium text-content-primary">{api.name}</div>
                </td>
                <td className="table-cell whitespace-nowrap">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-semibold font-mono-nums border ${getMethodStyle(api.method)}`}>
                    {api.method}
                  </span>
                </td>
                <td className="table-cell">
                  <div className="text-xs text-content-tertiary font-mono-nums truncate max-w-[200px]">
                    {api.url}
                  </div>
                </td>
                <td className="table-cell whitespace-nowrap">
                  <StatusBadge status={api.is_active ? 'active' : 'inactive'} />
                </td>
                <td className="table-cell whitespace-nowrap">
                  <span className={`text-xs font-mono-nums font-medium ${
                    api.uptime_percentage >= 99 ? 'text-success' :
                    api.uptime_percentage >= 95 ? 'text-warning' :
                      'text-danger'
                  }`}>
                    {formatPercentage(api.uptime_percentage)}
                  </span>
                </td>
                <td className="table-cell whitespace-nowrap text-xs text-content-tertiary font-mono-nums">
                  {api.avg_response_time ? formatDuration(api.avg_response_time) : '-'}
                </td>
                <td className="table-cell whitespace-nowrap text-xs text-content-tertiary font-mono-nums">
                  {api.updated_at ? formatDateTime(api.updated_at) : '-'}
                </td>
                <td className="table-cell whitespace-nowrap text-right text-xs">
                  <Link 
                    to={`/apis/${api.id}`} 
                    className="text-primary hover:text-primary-light transition-colors font-medium"
                  >
                    View
                  </Link>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}


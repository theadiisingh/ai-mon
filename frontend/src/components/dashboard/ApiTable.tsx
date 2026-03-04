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
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="card p-12 text-center flex flex-col items-center justify-center border-dashed"
      >
        <div className="w-12 h-12 bg-surface-700 rounded-full flex items-center justify-center mb-4">
          <Search className="h-5 w-5 text-content-tertiary" />
        </div>
        <h3 className="text-sm font-semibold text-content-primary">No APIs Registered</h3>
        <p className="mt-1 text-xs text-content-secondary max-w-xs">Add a new API endpoint to begin monitoring.</p>
        <div className="mt-5">
          <Link to="/apis/new" className="btn btn-primary text-xs">
            Add New API
          </Link>
        </div>
      </motion.div>
    )
  }

  const getMethodStyle = (method: string) => {
    switch (method) {
      case 'GET': return 'bg-surface-700 text-surface-300 border-surface-600'
      case 'POST': return 'bg-surface-700 text-surface-300 border-surface-600'
      case 'PUT': return 'bg-surface-700 text-surface-300 border-surface-600'
      case 'DELETE': return 'bg-surface-700 text-surface-300 border-surface-600'
      case 'PATCH': return 'bg-surface-700 text-surface-300 border-surface-600'
      default: return 'bg-surface-700 text-surface-400 border-surface-600'
    }
  }

  return (
    <div className="card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-border">
          <thead className="bg-surface-800">
            <tr>
              <th className="px-4 py-3 text-left text-[11px] font-semibold text-content-tertiary uppercase tracking-wider">Endpoint</th>
              <th className="px-4 py-3 text-left text-[11px] font-semibold text-content-tertiary uppercase tracking-wider">Method</th>
              <th className="px-4 py-3 text-left text-[11px] font-semibold text-content-tertiary uppercase tracking-wider">URL</th>
              <th className="px-4 py-3 text-left text-[11px] font-semibold text-content-tertiary uppercase tracking-wider">Status</th>
              <th className="px-4 py-3 text-left text-[11px] font-semibold text-content-tertiary uppercase tracking-wider">Uptime</th>
              <th className="px-4 py-3 text-left text-[11px] font-semibold text-content-tertiary uppercase tracking-wider">Avg Response</th>
              <th className="px-4 py-3 text-left text-[11px] font-semibold text-content-tertiary uppercase tracking-wider">Last Check</th>
              <th className="px-4 py-3 text-right text-[11px] font-semibold text-content-tertiary uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {apis.map((api, index) => (
              <motion.tr 
                key={api.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: index * 0.03 }}
                className="hover:bg-surface-800/50 transition-colors duration-150"
              >
                <td className="px-4 py-3 whitespace-nowrap">
                  <div className="text-sm font-medium text-content-primary">{api.name}</div>
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${getMethodStyle(api.method)}`}>
                    {api.method}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="text-xs text-content-secondary font-mono truncate max-w-xs">
                    {api.url}
                  </div>
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <StatusBadge status={api.is_active ? 'active' : 'inactive'} />
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <span className={`text-xs font-mono font-medium ${
                    api.uptime_percentage >= 99 ? 'text-success' :
                    api.uptime_percentage >= 95 ? 'text-warning' :
                      'text-danger'
                  }`}>
                    {formatPercentage(api.uptime_percentage)}
                  </span>
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-xs text-content-secondary font-mono">
                  {api.avg_response_time ? formatDuration(api.avg_response_time) : '-'}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-xs text-content-tertiary font-mono">
                  {api.updated_at ? formatDateTime(api.updated_at) : '-'}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-right text-xs">
                  <Link 
                    to={`/apis/${api.id}`} 
                    className="text-primary hover:text-primary-light transition-colors"
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


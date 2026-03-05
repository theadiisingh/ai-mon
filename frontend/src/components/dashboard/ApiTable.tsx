import { Link } from 'react-router-dom'
import { ApiEndpoint } from '../../types/api'
import StatusBadge from './StatusBadge'
import { formatPercentage, formatDuration, formatDateTime } from '../../utils/formatters'
import { Plus, Activity } from 'lucide-react'
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
        transition={{ duration: 0.2 }}
        className="card p-12 text-center flex flex-col items-center justify-center border-dashed border border-white/5"
      >
        {/* Professional empty state illustration */}
        <div className="relative mb-6">
          <div className="w-16 h-16 bg-gradient-to-br from-primary/10 to-primary/5 rounded-2xl flex items-center justify-center border border-primary/10">
            <Activity className="w-7 h-7 text-primary" />
          </div>
          <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-surface-800 rounded-lg border border-white/5 flex items-center justify-center">
            <Plus className="w-3 h-3 text-content-tertiary" />
          </div>
        </div>
        
        <h3 className="text-base font-semibold text-content-primary mb-2">No endpoints registered</h3>
        <p className="text-sm text-content-tertiary max-w-xs mb-6">
          Start monitoring your APIs by adding your first endpoint. We'll track uptime, latency, and performance.
        </p>
        <Link 
          to="/apis/new" 
          className="btn btn-primary text-sm px-5 py-2.5 flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add Your First Endpoint
        </Link>
      </motion.div>
    )
  }

  const getMethodStyle = (method: string) => {
    const baseStyle = 'bg-primary/10 border-primary/20'
    const methodColors: Record<string, string> = {
      GET: 'text-blue-400 border-blue-500/20 bg-blue-500/10',
      POST: 'text-emerald-400 border-emerald-500/20 bg-emerald-500/10',
      PUT: 'text-amber-400 border-amber-500/20 bg-amber-500/10',
      DELETE: 'text-red-400 border-red-500/20 bg-red-500/10',
      PATCH: 'text-purple-400 border-purple-500/20 bg-purple-500/10',
    }
    return methodColors[method] || baseStyle
  }

  return (
    <div className="card overflow-hidden" style={{ boxShadow: '0 4px 24px rgba(0, 0, 0, 0.15)' }}>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-white/5">
          <thead className="bg-surface-800/40 backdrop-blur-sm">
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
          <tbody className="divide-y divide-white/5 bg-surface-800/20">
            {apis.map((api, index) => (
              <motion.tr 
                key={api.id}
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.03, duration: 0.15 }}
                className="hover:bg-white/[0.02] transition-colors duration-150 group"
              >
                <td className="table-cell whitespace-nowrap">
                  <div className="text-sm font-medium text-content-primary group-hover:text-primary transition-colors duration-150">{api.name}</div>
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
                  <StatusBadge status={!api.status ? 'unknown' : api.status === 'DOWN' ? 'down' : 'up'} />
                </td>
                <td className="table-cell whitespace-nowrap">
                  <span className={`text-xs font-mono-nums font-medium ${
                    api.uptime_percentage >= 99 ? 'text-emerald-500' :
                    api.uptime_percentage >= 95 ? 'text-amber-500' :
                      'text-red-500'
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
                    className="text-primary hover:text-primary-light transition-colors duration-150 font-medium inline-flex items-center gap-1"
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


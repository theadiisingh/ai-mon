import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { apiApi } from '../api/apiApi'
import { metricsApi } from '../api/metricsApi'
import { ApiEndpoint } from '../types/api'
import { Metrics, Uptime } from '../types/monitoring'
import ResponseTimeChart from '../components/charts/ResponseTimeChart'
import UptimeChart from '../components/charts/UptimeChart'
import LogsTable from '../components/logs/LogsTable'
import AiInsightPanel from '../components/logs/AiInsightPanel'
import StatCard from '../components/dashboard/StatCard'
import { formatPercentage, formatDuration, getUptimeStatus } from '../utils/formatters'
import { motion, Variants } from 'framer-motion'
import { Play, Pause, Trash2, Activity, Clock, Server, BarChart3, ChevronRight } from 'lucide-react'

const containerVariants: Variants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05
    }
  }
}

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 8 },
  show: { opacity: 1, y: 0 }
}

const methodColors: Record<string, string> = {
  GET: 'bg-surface-700 text-surface-300 border-surface-600',
  POST: 'bg-surface-700 text-surface-300 border-surface-600',
  PUT: 'bg-surface-700 text-surface-300 border-surface-600',
  DELETE: 'bg-surface-700 text-surface-300 border-surface-600',
  PATCH: 'bg-surface-700 text-surface-300 border-surface-600',
}

export default function ApiDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [analyzing, setAnalyzing] = useState(false)

  const endpointId = Number(id)

  // Fetch endpoint details
  const { data: apiData, isLoading: apiLoading } = useQuery({
    queryKey: ['api', id],
    queryFn: async () => {
      const response = await apiApi.get(endpointId)
      return response.data
    },
    enabled: !!id,
  })

  // Fetch metrics from backend - NO calculation in frontend
  const { data: metricsData, isLoading: metricsLoading } = useQuery({
    queryKey: ['metrics', id],
    queryFn: async () => {
      const response = await metricsApi.getMetrics(endpointId, 24)
      return response.data
    },
    enabled: !!id,
  })

  const { data: logsData } = useQuery({
    queryKey: ['logs', id],
    queryFn: async () => {
      const response = await metricsApi.getLogs({ api_endpoint_id: endpointId, page_size: 50 })
      return response.data.items
    },
    enabled: !!id,
  })

  const { data: insightsData } = useQuery({
    queryKey: ['insights', id],
    queryFn: async () => {
      const response = await metricsApi.getInsights(endpointId)
      return response.data
    },
    enabled: !!id,
  })

  const deleteMutation = useMutation({
    mutationFn: () => apiApi.delete(endpointId),
    onSuccess: () => {
      navigate('/dashboard')
    },
  })

  const toggleMutation = useMutation({
    mutationFn: () => apiApi.toggle(endpointId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api', id] })
    },
  })

  const analyzeMutation = useMutation({
    mutationFn: () => metricsApi.triggerAnalysis(endpointId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['insights', id] })
    },
  })

  const handleAnalyze = () => {
    setAnalyzing(true)
    analyzeMutation.mutate(undefined, {
      onSettled: () => setAnalyzing(false),
    })
  }

  if (apiLoading) {
    return (
      <div className="space-y-6">
        <div className="h-7 w-48 bg-surface-700 rounded animate-pulse"></div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="card p-4 animate-pulse">
              <div className="h-3 w-24 bg-surface-700 rounded mb-3"></div>
              <div className="h-6 w-16 bg-surface-700 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (!apiData) {
    return (
      <div className="text-center py-16 px-6">
        <div className="w-12 h-12 bg-surface-700 rounded-full flex items-center justify-center mx-auto mb-4">
          <Server className="h-5 w-5 text-content-tertiary" />
        </div>
        <h3 className="text-sm font-medium text-content-primary mb-1">Endpoint Not Found</h3>
        <p className="text-xs text-content-secondary mb-5">The API endpoint you are looking for might have been deleted.</p>
        <button onClick={() => navigate('/dashboard')} className="btn btn-primary text-xs">Return to Dashboard</button>
      </div>
    )
  }

  const api: ApiEndpoint = apiData
  // Get uptime directly from backend - NO calculation
  const metrics: Metrics = metricsData || {
    total_checks: 0,
    successful_checks: 0,
    failed_checks: 0,
    error_rate: 0,
    uptime_percentage: 0,
    avg_response_time: 0,
    min_response_time: 0,
    max_response_time: 0,
  }

  // Get uptime status using centralized utility
  const uptimeStatus = getUptimeStatus(metrics.uptime_percentage)

  const uptimeData: Uptime | null = metrics ? {
    total_checks: metrics.total_checks,
    successful_checks: metrics.successful_checks,
    uptime_percentage: metrics.uptime_percentage
  } : null

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="space-y-6"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="flex flex-col md:flex-row md:items-start justify-between gap-4 pb-5 border-b border-border">
        <div>
          <div className="flex items-center text-xs text-content-secondary mb-3">
            <button onClick={() => navigate('/dashboard')} className="hover:text-content-primary transition-colors">Dashboard</button>
            <ChevronRight className="w-3.5 h-3.5 mx-1 text-content-tertiary" />
            <span className="text-content-primary truncate max-w-[200px]">{api.name}</span>
          </div>
          <div className="flex items-center flex-wrap gap-2">
            <h1 className="text-lg font-semibold text-content-primary">{api.name}</h1>
            <span className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${methodColors[api.method] || 'bg-surface-700 text-surface-400 border-surface-600'}`}>
              {api.method}
            </span>
            <span className="flex items-center text-xs">
              <span className={`relative inline-flex rounded-full h-2 w-2 ${api.is_active ? 'bg-success' : 'bg-warning'}`}></span>
              <span className={`ml-2 ${api.is_active ? 'text-success' : 'text-warning'}`}>
                {api.is_active ? 'Active' : 'Paused'}
              </span>
            </span>
          </div>
          <div className="flex items-center mt-2 p-2 bg-surface-800 border border-border rounded inline-flex max-w-full">
            <code className="text-xs font-mono text-content-secondary truncate">{api.url}</code>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={() => toggleMutation.mutate()}
            className="btn btn-secondary flex items-center gap-2 text-xs px-3 py-1.5"
          >
            {api.is_active ? (
              <><Pause className="w-3.5 h-3.5" /> Pause</>
            ) : (
              <><Play className="w-3.5 h-3.5" /> Resume</>
            )}
          </button>
          <button
            onClick={() => {
              if (window.confirm('Are you sure you want to delete this endpoint?')) {
                deleteMutation.mutate()
              }
            }}
            className="btn btn-secondary border-danger/30 text-danger hover:bg-danger/10 text-xs px-3 py-1.5 flex items-center gap-2"
          >
            <Trash2 className="w-3.5 h-3.5" /> Delete
          </button>
        </div>
      </motion.div>

      {/* Stats Cards - All data from backend API */}
      <motion.div variants={containerVariants} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <motion.div variants={itemVariants}>
          <StatCard
            title="Monitoring Status"
            value={api.is_active ? 'Active' : 'Paused'}
            color={api.is_active ? 'success' : 'warning'}
            icon={<Activity className="w-4 h-4" />}
          />
        </motion.div>
        <motion.div variants={itemVariants}>
          <StatCard
            title="System Uptime"
            value={formatPercentage(metrics.uptime_percentage)}
            subtitle="Trailing 24 hours"
            color={uptimeStatus}
            icon={<Server className="w-4 h-4" />}
          />
        </motion.div>
        <motion.div variants={itemVariants}>
          <StatCard
            title="Avg Response Time"
            value={formatDuration(metrics.avg_response_time)}
            subtitle="Across all checks"
            icon={<Clock className="w-4 h-4" />}
          />
        </motion.div>
        <motion.div variants={itemVariants}>
          <StatCard
            title="Total Health Checks"
            value={metrics.total_checks}
            subtitle="Since creation"
            icon={<BarChart3 className="w-4 h-4" />}
          />
        </motion.div>
      </motion.div>

      {/* Charts */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ResponseTimeChart data={[]} loading={metricsLoading} />
        <UptimeChart uptime={uptimeData} loading={metricsLoading} />
      </motion.div>

      {/* AI Insights & Logs */}
      <motion.div variants={containerVariants} className="space-y-6">
        <motion.div variants={itemVariants}>
          <AiInsightPanel
            insights={insightsData || []}
            onAnalyze={handleAnalyze}
            analyzing={analyzing}
          />
        </motion.div>

        <motion.div variants={itemVariants}>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-content-primary">Recent Activity Logs</h2>
          </div>
          <LogsTable logs={logsData || []} />
        </motion.div>
      </motion.div>
    </motion.div>
  )
}


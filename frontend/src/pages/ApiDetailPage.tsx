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
import { formatPercentage, formatDuration } from '../utils/formatters'
import { motion, Variants } from 'framer-motion'
import { Play, Pause, Trash2, Activity, Clock, Server, BarChart3, ChevronRight } from 'lucide-react'

const containerVariants: Variants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
}

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
}

const methodColors: Record<string, string> = {
  GET: 'bg-blue-100 text-blue-700 ring-1 ring-blue-700/10',
  POST: 'bg-green-100 text-green-700 ring-1 ring-green-700/10',
  PUT: 'bg-amber-100 text-amber-700 ring-1 ring-amber-700/10',
  DELETE: 'bg-red-100 text-red-700 ring-1 ring-red-700/10',
  PATCH: 'bg-purple-100 text-purple-700 ring-1 ring-purple-700/10',
  DEFAULT: 'bg-zinc-100 text-zinc-700 ring-1 ring-zinc-700/10'
}

export default function ApiDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [analyzing, setAnalyzing] = useState(false)

  const { data: apiData, isLoading: apiLoading } = useQuery<{ data: ApiEndpoint }>({
    queryKey: ['api', id],
    queryFn: async () => {
      const response = await apiApi.get(Number(id!))
      return response
    },
    enabled: !!id,
  })

  const { data: metricsData, isLoading: metricsLoading } = useQuery<{ data: Metrics }>({
    queryKey: ['metrics', id],
    queryFn: async () => {
      const response = await metricsApi.getMetrics(Number(id!))
      return response
    },
    enabled: !!id,
  })

  const { data: logsData } = useQuery({
    queryKey: ['logs', id],
    queryFn: async () => {
      const response = await metricsApi.getLogs({ api_endpoint_id: Number(id), page_size: 50 })
      return response.data.items
    },
    enabled: !!id,
  })

  const { data: insightsData } = useQuery({
    queryKey: ['insights', id],
    queryFn: async () => {
      const response = await metricsApi.getInsights(Number(id!))
      return response.data
    },
    enabled: !!id,
  })

  const deleteMutation = useMutation({
    mutationFn: () => apiApi.delete(Number(id!)),
    onSuccess: () => {
      navigate('/dashboard')
    },
  })

  const toggleMutation = useMutation({
    mutationFn: () => apiApi.toggle(Number(id!)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api', id] })
    },
  })

  const analyzeMutation = useMutation({
    mutationFn: () => metricsApi.triggerAnalysis(Number(id!)),
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
        <div className="h-8 w-64 bg-zinc-200 rounded-md animate-pulse"></div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="card p-6 animate-pulse bg-white">
              <div className="h-4 w-24 bg-zinc-100 rounded mb-4"></div>
              <div className="h-8 w-16 bg-zinc-200 rounded"></div>
            </div>
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card h-80 animate-pulse bg-white"></div>
          <div className="card h-80 animate-pulse bg-white"></div>
        </div>
      </div>
    )
  }

  if (!apiData) {
    return (
      <div className="text-center py-20 px-6">
        <div className="w-16 h-16 bg-zinc-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Server className="h-8 w-8 text-zinc-400" />
        </div>
        <h3 className="text-lg font-medium text-zinc-900 mb-1">Endpoint Not Found</h3>
        <p className="text-zinc-500 mb-6">The API endpoint you are looking for might have been deleted or doesn't exist.</p>
        <button onClick={() => navigate('/dashboard')} className="btn btn-primary">Return to Dashboard</button>
      </div>
    )
  }

  const api: ApiEndpoint = apiData.data
  const metrics: Metrics = metricsData?.data || {
    total_checks: api.total_checks || 0,
    successful_checks: api.successful_checks || 0,
    failed_checks: api.failed_checks || 0,
    error_rate: 0,
    uptime_percentage: api.uptime_percentage || 0,
    avg_response_time: api.avg_response_time || 0,
    min_response_time: 0,
    max_response_time: 0,
  }

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
      className="space-y-8"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="flex flex-col md:flex-row md:items-start justify-between gap-6 pb-6 border-b border-zinc-200/60">
        <div>
          <div className="flex items-center text-sm font-medium text-zinc-500 mb-3">
            <button onClick={() => navigate('/dashboard')} className="hover:text-zinc-900 transition-colors">Dashboard</button>
            <ChevronRight className="w-4 h-4 mx-1 text-zinc-300" />
            <span className="text-zinc-900 truncate max-w-[200px] sm:max-w-xs">{api.name}</span>
          </div>
          <div className="flex items-center flex-wrap gap-3">
            <h1 className="text-2xl sm:text-3xl font-bold text-zinc-900 tracking-tight">{api.name}</h1>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${methodColors[api.method] || methodColors.DEFAULT}`}>
              {api.method}
            </span>
            <span className="flex items-center text-sm">
              <span className={`relative flex h-2 w-2 mr-2`}>
                {api.is_active && (
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success-400 opacity-75"></span>
                )}
                <span className={`relative inline-flex rounded-full h-2 w-2 ${api.is_active ? 'bg-success-500' : 'bg-warning-500'
                  }`}></span>
              </span>
              <span className={`font-medium ${api.is_active ? 'text-success-700' : 'text-warning-700'}`}>
                {api.is_active ? 'Active' : 'Paused'}
              </span>
            </span>
          </div>
          <div className="flex items-center mt-3 p-2 bg-zinc-50 border border-zinc-200/80 rounded-lg inline-flex">
            <code className="text-sm font-mono text-zinc-600 truncate max-w-full sm:max-w-md">{api.url}</code>
          </div>
        </div>
        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={() => toggleMutation.mutate()}
            className="btn btn-secondary flex items-center gap-2 shadow-sm text-zinc-700 bg-white"
          >
            {api.is_active ? (
              <><Pause className="w-4 h-4" /> Pause Monitoring</>
            ) : (
              <><Play className="w-4 h-4" /> Resume Monitoring</>
            )}
          </button>
          <button
            onClick={() => {
              if (window.confirm('Are you sure you want to delete this endpoint?')) {
                deleteMutation.mutate()
              }
            }}
            className="btn btn-secondary border-red-200 text-red-700 hover:bg-red-50 hover:border-red-300 shadow-sm flex items-center gap-2 bg-white"
          >
            <Trash2 className="w-4 h-4" /> Delete
          </button>
        </div>
      </motion.div>

      {/* Stats Cards */}
      <motion.div variants={containerVariants} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 xl:gap-6">
        <motion.div variants={itemVariants}>
          <StatCard
            title="Monitoring Status"
            value={api.is_active ? 'Active' : 'Paused'}
            color={api.is_active ? 'success' : 'warning'}
            icon={<Activity className="w-5 h-5" />}
          />
        </motion.div>
        <motion.div variants={itemVariants}>
          <StatCard
            title="System Uptime"
            value={formatPercentage(metrics.uptime_percentage)}
            subtitle="Trailing 24 hours"
            color={metrics.uptime_percentage >= 99 ? 'success' : metrics.uptime_percentage >= 95 ? 'warning' : 'danger'}
            icon={<Server className="w-5 h-5" />}
          />
        </motion.div>
        <motion.div variants={itemVariants}>
          <StatCard
            title="Avg Response Time"
            value={formatDuration(metrics.avg_response_time)}
            subtitle="Across all regions"
            icon={<Clock className="w-5 h-5" />}
          />
        </motion.div>
        <motion.div variants={itemVariants}>
          <StatCard
            title="Total Health Checks"
            value={metrics.total_checks}
            subtitle="Since creation"
            icon={<BarChart3 className="w-5 h-5" />}
          />
        </motion.div>
      </motion.div>

      {/* Charts */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ResponseTimeChart data={[]} loading={metricsLoading} />
        <UptimeChart uptime={uptimeData} loading={metricsLoading} />
      </motion.div>

      {/* AI Insights & Logs */}
      <motion.div variants={containerVariants} className="space-y-6 lg:space-y-8">
        <motion.div variants={itemVariants}>
          <AiInsightPanel
            insights={insightsData || []}
            onAnalyze={handleAnalyze}
            analyzing={analyzing}
          />
        </motion.div>

        <motion.div variants={itemVariants}>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-zinc-900 tracking-tight">Recent Activity Logs</h2>
          </div>
          <LogsTable logs={logsData || []} />
        </motion.div>
      </motion.div>
    </motion.div>
  )
}

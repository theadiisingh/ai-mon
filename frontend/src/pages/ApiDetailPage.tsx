import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { apiApi } from '../api/apiApi'
import { metricsApi } from '../api/metricsApi'
import ResponseTimeChart from '../components/charts/ResponseTimeChart'
import UptimeChart from '../components/charts/UptimeChart'
import LogsTable from '../components/logs/LogsTable'
import AiInsightPanel from '../components/logs/AiInsightPanel'
import StatCard from '../components/dashboard/StatCard'
import StatusBadge from '../components/dashboard/StatusBadge'
import { formatPercentage, formatDuration, formatDateTime } from '../utils/formatters'

export default function ApiDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [analyzing, setAnalyzing] = useState(false)

  const { data: apiData, isLoading: apiLoading } = useQuery({
    queryKey: ['api', id],
    queryFn: async () => {
      const response = await apiApi.get(id!)
      return response.data
    },
    enabled: !!id,
  })

  const { data: metricsData, isLoading: metricsLoading } = useQuery({
    queryKey: ['metrics', id],
    queryFn: async () => {
      const response = await metricsApi.getMetrics(id!)
      return response.data
    },
    enabled: !!id,
  })

  const { data: logsData } = useQuery({
    queryKey: ['logs', id],
    queryFn: async () => {
      const response = await metricsApi.getLogs({ endpoint_id: Number(id), page_size: 50 })
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
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!apiData) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">API not found</p>
      </div>
    )
  }

  const api = apiData
  const metrics = metricsData || {}

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => navigate('/dashboard')}
              className="text-gray-500 hover:text-gray-700"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <h1 className="text-2xl font-bold text-gray-900">{api.name}</h1>
            <span className={`px-2 py-1 rounded text-xs font-medium ${
              api.method === 'GET' ? 'bg-blue-100 text-blue-700' :
              api.method === 'POST' ? 'bg-green-100 text-green-700' :
              api.method === 'PUT' ? 'bg-orange-100 text-orange-700' :
              api.method === 'DELETE' ? 'bg-red-100 text-red-700' :
              'bg-gray-100 text-gray-700'
            }`}>
              {api.method}
            </span>
          </div>
          <p className="text-gray-500 mt-1 font-mono text-sm">{api.url}</p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => toggleMutation.mutate()}
            className="btn btn-secondary"
          >
            {api.is_active ? 'Pause' : 'Resume'}
          </button>
          <button
            onClick={() => deleteMutation.mutate()}
            className="btn btn-danger"
          >
            Delete
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard
          title="Status"
          value={<StatusBadge status={api.is_active ? 'active' : 'inactive'} />}
          color={api.is_active ? 'success' : 'warning'}
        />
        <StatCard
          title="Uptime (24h)"
          value={formatPercentage(metrics.uptime?.uptime_percentage || 0)}
          color={(metrics.uptime?.uptime_percentage || 0) >= 99 ? 'success' : 'danger'}
        />
        <StatCard
          title="Avg Response"
          value={formatDuration(metrics.avg_response_time || 0)}
        />
        <StatCard
          title="Total Checks"
          value={metrics.uptime?.total_checks || 0}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ResponseTimeChart data={metrics.response_times || []} loading={metricsLoading} />
        <UptimeChart uptime={metrics.uptime} loading={metricsLoading} />
      </div>

      {/* AI Insights */}
      <AiInsightPanel
        insights={insightsData || []}
        onAnalyze={handleAnalyze}
        analyzing={analyzing}
      />

      {/* Logs */}
      <LogsTable logs={logsData || []} />
    </div>
  )
}

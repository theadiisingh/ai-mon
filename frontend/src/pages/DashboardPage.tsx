import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { apiApi } from '../api/apiApi'
import ApiTable from '../components/dashboard/ApiTable'
import StatCard from '../components/dashboard/StatCard'
import { formatPercentage } from '../utils/formatters'
import { ApiEndpoint } from '../types/api'
import { useAuth } from '../hooks/useAuth'
import { Activity, Server, Clock, Zap, Plus, RefreshCw, AlertCircle } from 'lucide-react'
import { motion, Variants } from 'framer-motion'

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

export default function DashboardPage() {
  const queryClient = useQueryClient()
  const { isAuthenticated, loading: authLoading } = useAuth()

  const { data: apisData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['apis'],
    queryFn: async () => {
      const response = await apiApi.list()
      return response.data
    },
    enabled: isAuthenticated && !authLoading,
    refetchInterval: 30000,
    staleTime: 10000,
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  })

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ['apis'] })
  }

  const apis: ApiEndpoint[] = apisData?.items || []

  const totalApis = apis.length
  const activeApis = apis.filter((api: ApiEndpoint) => api.is_active).length
  const avgUptime = totalApis > 0
    ? apis.reduce((sum: number, api: ApiEndpoint) => sum + api.uptime_percentage, 0) / totalApis
    : 0
  const avgResponseTime = totalApis > 0
    ? apis.reduce((sum: number, api: ApiEndpoint) => sum + (api.avg_response_time || 0), 0) / totalApis
    : 0

  if (authLoading || (isLoading && !apisData)) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="h-8 w-48 bg-zinc-200 rounded-md animate-pulse"></div>
            <div className="h-4 w-64 bg-zinc-100 rounded-md animate-pulse mt-2"></div>
          </div>
          <div className="h-10 w-24 bg-zinc-200 rounded-lg animate-pulse"></div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="card p-6 animate-pulse bg-white">
              <div className="h-4 w-24 bg-zinc-100 rounded mb-4"></div>
              <div className="h-8 w-16 bg-zinc-200 rounded mb-2"></div>
              <div className="h-3 w-32 bg-zinc-50 rounded"></div>
            </div>
          ))}
        </div>

        <div className="card overflow-hidden h-96">
          <div className="animate-pulse bg-zinc-50/50 h-full w-full p-6">
            <div className="h-10 bg-zinc-200 rounded-md bg-opacity-50 mb-6"></div>
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-6 bg-zinc-100 rounded-md w-full"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (isError) {
    const errorMessage = error instanceof Error ? error.message : 'An error occurred while loading your APIs'
    const isAuthError = errorMessage.includes('401') || errorMessage.includes('Unauthorized') || errorMessage.includes('credentials')

    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-zinc-900 tracking-tight">Dashboard</h1>
            <p className="text-zinc-500 mt-1">Monitor your APIs in real-time</p>
          </div>
        </div>

        <div className="bg-red-50/50 border border-red-200/60 rounded-xl p-8 text-center max-w-2xl mx-auto mt-12 shadow-sm">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="h-8 w-8 text-red-600" />
          </div>
          <h3 className="text-xl font-bold text-zinc-900">
            {isAuthError ? 'Authentication Session Expired' : 'Failed to load monitoring data'}
          </h3>
          <p className="mt-2 text-zinc-600">
            {isAuthError
              ? 'Your secure session may have expired. Please log in again to continue.'
              : errorMessage}
          </p>
          <div className="mt-8 flex justify-center gap-3">
            {isAuthError && (
              <Link to="/login" className="btn btn-primary">
                Return to Login
              </Link>
            )}
            <button onClick={() => refetch()} className="btn btn-secondary border-red-200 text-red-700 hover:bg-red-50">
              Try Again
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="space-y-8"
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <motion.div variants={itemVariants}>
          <h1 className="text-2xl font-bold text-zinc-900 tracking-tight">System Outline</h1>
          <p className="text-sm text-zinc-500 mt-1">Real-time status of all your connected services</p>
        </motion.div>
        <motion.div variants={itemVariants} className="flex items-center gap-3">
          <button
            onClick={handleRefresh}
            disabled={isFetching}
            className="btn btn-secondary flex items-center gap-2 text-zinc-600 px-3 hover:text-zinc-900"
            title="Refresh data"
          >
            <RefreshCw className={`w-4 h-4 ${isFetching ? 'animate-spin text-primary-500' : ''}`} />
            <span className="hidden sm:inline text-sm">{isFetching ? 'Syncing...' : 'Sync'}</span>
          </button>
          <Link to="/apis/new" className="btn btn-primary flex items-center gap-2 shadow-sm hover:shadow-primary-100 px-4">
            <Plus className="w-4 h-4" />
            <span className="text-sm">Add Endpoint</span>
          </Link>
        </motion.div>
      </div>

      {/* Stats Cards */}
      <motion.div variants={containerVariants} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 xl:gap-6">
        <motion.div variants={itemVariants}>
          <StatCard
            title="Total Endpoints"
            value={totalApis}
            icon={<Server className="w-6 h-6" />}
            color="primary"
          />
        </motion.div>
        <motion.div variants={itemVariants}>
          <StatCard
            title="Active Endpoints"
            value={activeApis}
            icon={<Activity className="w-6 h-6" />}
            color="success"
          />
        </motion.div>
        <motion.div variants={itemVariants}>
          <StatCard
            title="System Availability"
            value={formatPercentage(avgUptime)}
            subtitle="Trailing 24 hours"
            icon={<Clock className="w-6 h-6" />}
            color={avgUptime >= 99 ? 'success' : avgUptime >= 95 ? 'warning' : 'danger'}
          />
        </motion.div>
        <motion.div variants={itemVariants}>
          <StatCard
            title="Avg Latency"
            value={`${avgResponseTime.toFixed(0)}ms`}
            subtitle="Global average"
            icon={<Zap className="w-6 h-6" />}
            color="primary"
          />
        </motion.div>
      </motion.div>

      {/* API Table */}
      <motion.div variants={itemVariants}>
        <div className="flex items-center justify-between mb-4 mt-8">
          <h2 className="text-lg font-bold text-zinc-900 tracking-tight">Monitored Endpoints</h2>
        </div>
        <ApiTable apis={apis} />
      </motion.div>
    </motion.div>
  )
}

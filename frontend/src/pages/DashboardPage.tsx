import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { apiApi } from '../api/apiApi'
import { metricsApi } from '../api/metricsApi'
import ApiTable from '../components/dashboard/ApiTable'
import StatCard from '../components/dashboard/StatCard'
import { formatPercentage, getUptimeStatus } from '../utils/formatters'
import { useAuth } from '../hooks/useAuth'
import { Activity, Server, Clock, Zap, Plus, RefreshCw, AlertCircle } from 'lucide-react'
import { motion, Variants } from 'framer-motion'

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
  show: { opacity: 1, y: 0, transition: { duration: 0.2, ease: [0.4, 0, 0.2, 1] } }
}

export default function DashboardPage() {
  const { isAuthenticated, loading: authLoading } = useAuth()

  // Fetch endpoints list for the table
  const { data: apisData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['apis'],
    queryFn: async () => {
      const response = await apiApi.list()
      return response.data
    },
    enabled: isAuthenticated && !authLoading,
  })

  // Fetch aggregated metrics from backend - NO calculation in frontend
  const { data: metricsData } = useQuery({
    queryKey: ['metrics', 'overview', 'all'],
    queryFn: async () => {
      const response = await metricsApi.getMetrics(undefined, 24)
      return response.data
    },
    enabled: isAuthenticated && !authLoading,
  })

  const apis = apisData?.items || []
  const totalApis = apis.length
  const activeApis = apis.filter((api) => api.is_active).length

  // Get uptime directly from backend - NO calculation
  const avgUptime = metricsData?.uptime_percentage ?? 0
  const avgResponseTime = metricsData?.avg_response_time ?? 0

  // Get uptime status for color using centralized utility
  const uptimeStatus = getUptimeStatus(avgUptime)

  const handleRefresh = () => {
    refetch()
  }

  if (authLoading || (isLoading && !apisData)) {
    return (
      <div className="space-y-5">
        <div className="flex items-center justify-between">
          <div>
            <div className="h-6 w-36 bg-surface-700 rounded animate-pulse"></div>
            <div className="h-4 w-48 bg-surface-800 rounded animate-pulse mt-2"></div>
          </div>
          <div className="h-9 w-20 bg-surface-700 rounded animate-pulse"></div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="card p-4 animate-pulse">
              <div className="h-2.5 w-16 bg-surface-700 rounded mb-3"></div>
              <div className="h-6 w-14 bg-surface-700 rounded"></div>
            </div>
          ))}
        </div>

        <div className="card overflow-hidden h-72">
          <div className="animate-pulse bg-surface-800 h-full w-full p-4">
            <div className="h-5 w-28 bg-surface-700 rounded mb-4"></div>
            <div className="space-y-2">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-7 bg-surface-700 rounded w-full"></div>
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
      <div className="space-y-5">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-content-primary">System Overview</h1>
            <p className="text-xs text-content-tertiary mt-1">Real-time status of all connected services</p>
          </div>
        </div>

        <div className="bg-danger/5 border border-danger/10 rounded-lg p-8 text-center max-w-lg mx-auto mt-12">
          <div className="w-10 h-10 bg-danger/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="h-5 w-5 text-danger" />
          </div>
          <h3 className="text-sm font-medium text-content-primary">
            {isAuthError ? 'Session Expired' : 'Failed to Load Intelligence'}
          </h3>
          <p className="mt-2 text-xs text-content-tertiary">
            {isAuthError
              ? 'Your session may have expired. Please authenticate again.'
              : errorMessage}
          </p>
          <div className="mt-5 flex justify-center gap-2">
            {isAuthError && (
              <Link to="/login" className="btn btn-primary text-xs">
                Sign In
              </Link>
            )}
            <button onClick={() => refetch()} className="btn btn-secondary text-xs">
              Retry
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
      className="space-y-5"
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <motion.div variants={itemVariants}>
          <h1 className="text-xl font-semibold text-content-primary">System Overview</h1>
          <p className="text-xs text-content-tertiary mt-0.5">Real-time status of all connected services</p>
        </motion.div>
        <motion.div variants={itemVariants} className="flex items-center gap-2">
          <button
            onClick={handleRefresh}
            disabled={isFetching}
            className="btn btn-secondary flex items-center gap-2 text-xs px-3 py-1.5"
            title="Refresh data"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">{isFetching ? 'Syncing...' : 'Sync'}</span>
          </button>
          <Link to="/apis/new" className="btn btn-primary flex items-center gap-2 text-xs px-3 py-1.5">
            <Plus className="w-3.5 h-3.5" />
            <span>Add Endpoint</span>
          </Link>
        </motion.div>
      </div>

      {/* Stats Cards - All data from backend API */}
      <motion.div variants={containerVariants} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <motion.div variants={itemVariants}>
          <StatCard
            title="Total Endpoints"
            value={totalApis}
            icon={<Server className="w-4 h-4" />}
            color="primary"
          />
        </motion.div>
        <motion.div variants={itemVariants}>
          <StatCard
            title="Active Endpoints"
            value={activeApis}
            icon={<Activity className="w-4 h-4" />}
            color="success"
          />
        </motion.div>
        <motion.div variants={itemVariants}>
          <StatCard
            title="System Availability"
            value={formatPercentage(avgUptime)}
            subtitle="Trailing 24 hours"
            icon={<Clock className="w-4 h-4" />}
            color={uptimeStatus}
          />
        </motion.div>
        <motion.div variants={itemVariants}>
          <StatCard
            title="Avg Latency"
            value={`${avgResponseTime.toFixed(2)}ms`}
            subtitle="Global average"
            icon={<Zap className="w-4 h-4" />}
            color="primary"
          />
        </motion.div>
      </motion.div>

      {/* API Table */}
      <motion.div variants={itemVariants}>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-medium text-content-primary">Monitored Endpoints</h2>
        </div>
        <ApiTable apis={apis} />
      </motion.div>
    </motion.div>
  )
}


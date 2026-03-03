import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { apiApi } from '../api/apiApi'
import ApiTable from '../components/dashboard/ApiTable'
import StatCard from '../components/dashboard/StatCard'
import { formatPercentage } from '../utils/formatters'
import { ApiEndpoint } from '../types/api'
import { useAuth } from '../hooks/useAuth'

export default function DashboardPage() {
  const queryClient = useQueryClient()
  const { isAuthenticated, loading: authLoading } = useAuth()

  // Fetch APIs with auto-refresh - only when authenticated
  const { data: apisData, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['apis'],
    queryFn: async () => {
      const response = await apiApi.list()
      return response.data
    },
    enabled: isAuthenticated && !authLoading, // Only fetch when authenticated
    refetchInterval: 30000, // Auto-refresh every 30 seconds
    staleTime: 10000, // Consider data stale after 10 seconds
    retry: 3, // Retry up to 3 times on failure
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  })

  // Manual refresh handler
  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ['apis'] })
  }

  const apis: ApiEndpoint[] = apisData?.items || []
  
  // Calculate aggregate stats
  const totalApis = apis.length
  const activeApis = apis.filter((api: ApiEndpoint) => api.is_active).length
  const avgUptime = totalApis > 0 
    ? apis.reduce((sum: number, api: ApiEndpoint) => sum + api.uptime_percentage, 0) / totalApis 
    : 0
  const avgResponseTime = totalApis > 0
    ? apis.reduce((sum: number, api: ApiEndpoint) => sum + (api.avg_response_time || 0), 0) / totalApis
    : 0

  // Show loading skeleton while auth is loading
  if (authLoading || (isLoading && !apisData)) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="h-8 w-48 bg-gray-200 rounded animate-pulse"></div>
            <div className="h-4 w-64 bg-gray-200 rounded animate-pulse mt-2"></div>
          </div>
          <div className="h-10 w-24 bg-gray-200 rounded animate-pulse"></div>
        </div>

        {/* Stats Cards Skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
              <div className="h-4 w-20 bg-gray-200 rounded mb-4"></div>
              <div className="h-8 w-16 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>

        {/* Table Skeleton */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="animate-pulse">
            <div className="h-12 bg-gray-100 border-b"></div>
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 border-b border-gray-100 flex items-center px-6 gap-4">
                <div className="h-4 w-32 bg-gray-200 rounded"></div>
                <div className="h-4 w-16 bg-gray-200 rounded"></div>
                <div className="h-4 w-48 bg-gray-200 rounded"></div>
                <div className="h-4 w-20 bg-gray-200 rounded"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  // Show error state with better error message
  if (isError) {
    const errorMessage = error instanceof Error ? error.message : 'An error occurred while loading your APIs'
    const isAuthError = errorMessage.includes('401') || errorMessage.includes('Unauthorized') || errorMessage.includes('credentials')
    
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-500">Monitor your APIs in real-time</p>
          </div>
        </div>

        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <svg className="mx-auto h-12 w-12 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <h3 className="mt-4 text-lg font-medium text-red-800">
            {isAuthError ? 'Authentication Error' : 'Failed to load dashboard'}
          </h3>
          <p className="mt-2 text-sm text-red-600">
            {isAuthError 
              ? 'Your session may have expired. Please try logging in again.' 
              : errorMessage}
          </p>
          <div className="mt-4 flex justify-center gap-3">
            {isAuthError && (
              <Link
                to="/login"
                className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
              >
                Go to Login
              </Link>
            )}
            <button
              onClick={() => refetch()}
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500">Monitor your APIs in real-time</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleRefresh}
            className="btn btn-secondary flex items-center gap-2"
            title="Refresh data"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
          <Link to="/apis/new" className="btn btn-primary flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add API
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard
          title="Total APIs"
          value={totalApis}
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          }
          color="primary"
        />
        <StatCard
          title="Active APIs"
          value={activeApis}
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
          color="success"
        />
        <StatCard
          title="Avg. Uptime"
          value={formatPercentage(avgUptime)}
          subtitle="Last 24 hours"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          }
          color={avgUptime >= 99 ? 'success' : avgUptime >= 95 ? 'warning' : 'danger'}
        />
        <StatCard
          title="Avg. Response"
          value={`${avgResponseTime.toFixed(0)}ms`}
          subtitle="Across all APIs"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
          color="primary"
        />
      </div>

      {/* API Table */}
      <ApiTable apis={apis} />
    </div>
  )
}

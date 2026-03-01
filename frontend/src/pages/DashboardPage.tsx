import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { apiApi } from '../api/apiApi'
import ApiTable from '../components/dashboard/ApiTable'
import StatCard from '../components/dashboard/StatCard'
import { formatPercentage, formatNumber } from '../utils/formatters'

export default function DashboardPage() {
  const { data: apisData, isLoading } = useQuery({
    queryKey: ['apis'],
    queryFn: async () => {
      const response = await apiApi.list()
      return response.data
    },
  })

  const apis = apisData?.items || []
  
  // Calculate aggregate stats
  const totalApis = apis.length
  const activeApis = apis.filter(api => api.is_active).length
  const avgUptime = totalApis > 0 
    ? apis.reduce((sum, api) => sum + api.uptime_percentage, 0) / totalApis 
    : 0
  const avgResponseTime = totalApis > 0
    ? apis.reduce((sum, api) => sum + (api.avg_response_time || 0), 0) / totalApis
    : 0

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500">Monitor your APIs in real-time</p>
        </div>
        <Link to="/apis/new" className="btn btn-primary">
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Add API
        </Link>
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

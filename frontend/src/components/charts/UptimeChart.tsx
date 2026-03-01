import { Uptime } from '../../types/monitoring'

interface UptimeChartProps {
  uptime: Uptime | null
  loading?: boolean
}

export default function UptimeChart({ uptime, loading }: UptimeChartProps) {
  if (loading) {
    return (
      <div className="card p-6 h-48 flex items-center justify-center">
        <div className="animate-pulse flex flex-col items-center">
          <div className="h-24 w-24 bg-gray-200 rounded-full"></div>
          <p className="mt-2 text-sm text-gray-500">Loading...</p>
        </div>
      </div>
    )
  }

  if (!uptime) {
    return (
      <div className="card p-6 h-48 flex items-center justify-center">
        <p className="text-sm text-gray-500">No data available</p>
      </div>
    )
  }

  const percentage = uptime.uptime_percentage
  const circumference = 2 * Math.PI * 40
  const strokeDashoffset = circumference - (percentage / 100) * circumference

  const getColor = () => {
    if (percentage >= 99) return '#22c55e' // green
    if (percentage >= 95) return '#f59e0b' // yellow
    return '#ef4444' // red
  }

  return (
    <div className="card p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Uptime (Last 24h)</h3>
      <div className="flex items-center justify-center">
        <div className="relative w-32 h-32">
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="64"
              cy="64"
              r="40"
              stroke="#e5e7eb"
              strokeWidth="8"
              fill="none"
            />
            <circle
              cx="64"
              cy="64"
              r="40"
              stroke={getColor()}
              strokeWidth="8"
              fill="none"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              className="transition-all duration-500"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-2xl font-bold" style={{ color: getColor() }}>
              {percentage.toFixed(1)}%
            </span>
          </div>
        </div>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-4 text-center">
        <div>
          <p className="text-sm text-gray-500">Total Checks</p>
          <p className="text-lg font-semibold text-gray-900">{uptime.total_checks}</p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Successful</p>
          <p className="text-lg font-semibold text-success-600">{uptime.successful_checks}</p>
        </div>
      </div>
    </div>
  )
}

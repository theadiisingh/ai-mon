import { Uptime } from '../../types/monitoring'

interface UptimeChartProps {
  uptime: Uptime | null
  loading?: boolean
}

export default function UptimeChart({ uptime, loading }: UptimeChartProps) {
  if (loading) {
    return (
      <div className="card shadow-sm border-zinc-200/60 p-6 h-[300px] flex items-center justify-center">
        <div className="animate-pulse flex flex-col items-center">
          <div className="h-32 w-32 bg-zinc-100/80 rounded-full"></div>
          <p className="mt-4 text-sm text-zinc-400 font-medium">Loading metrics...</p>
        </div>
      </div>
    )
  }

  if (!uptime) {
    return (
      <div className="card shadow-sm border-zinc-200/60 p-8 h-[300px] flex flex-col items-center justify-center">
        <div className="w-12 h-12 bg-zinc-50 rounded-full flex items-center justify-center mb-3">
          <svg className="w-6 h-6 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <p className="text-sm font-medium text-zinc-900 mb-1">No uptime data</p>
        <p className="text-xs text-zinc-500">Wait for the monitoring service to record uptime.</p>
      </div>
    )
  }

  const percentage = uptime.uptime_percentage
  const radius = 56
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (percentage / 100) * circumference

  const getColor = () => {
    if (percentage >= 99) return '#10b981' // emerald-500
    if (percentage >= 95) return '#f59e0b' // amber-500
    return '#ef4444' // red-500
  }

  return (
    <div className="card shadow-sm border-zinc-200/60 p-6 h-[300px] flex flex-col">
      <h3 className="text-base font-bold text-zinc-900 tracking-tight mb-6">Uptime (Last 24h)</h3>
      <div className="flex-1 flex flex-col items-center justify-center">
        <div className="relative w-40 h-40">
          {/* Background circle */}
          <svg className="w-full h-full transform -rotate-90 drop-shadow-sm">
            <circle
              cx="80"
              cy="80"
              r={radius}
              stroke="#f4f4f5" // zinc-100
              strokeWidth="12"
              fill="none"
            />
            {/* Progress circle */}
            <circle
              cx="80"
              cy="80"
              r={radius}
              stroke={getColor()}
              strokeWidth="12"
              fill="none"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              className="transition-all duration-1000 ease-out"
            />
          </svg>
          {/* Inner text */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-3xl font-bold tracking-tight" style={{ color: getColor() }}>
              {percentage.toFixed(1)}%
            </span>
            <span className="text-xs font-medium text-zinc-400 uppercase tracking-widest mt-1">
              Uptime
            </span>
          </div>
        </div>

        {/* Footer Stats */}
        <div className="mt-8 flex items-center justify-center gap-8 w-full">
          <div className="text-center">
            <p className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-1">Checks</p>
            <p className="text-xl font-bold text-zinc-900">{uptime.total_checks}</p>
          </div>
          <div className="w-px h-8 bg-zinc-200/80"></div>
          <div className="text-center">
            <p className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-1">Success</p>
            <p className="text-xl font-bold text-success-600">{uptime.successful_checks}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

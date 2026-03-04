import { Uptime } from '../../types/monitoring'

interface UptimeChartProps {
  uptime: Uptime | null
  loading?: boolean
}

export default function UptimeChart({ uptime, loading }: UptimeChartProps) {
  if (loading) {
    return (
      <div className="card p-4 h-[300px] flex items-center justify-center">
        <div className="animate-pulse flex flex-col items-center">
          <div className="h-32 w-32 bg-surface-700/50 rounded-full"></div>
          <p className="mt-4 text-xs text-content-tertiary font-medium">Loading metrics...</p>
        </div>
      </div>
    )
  }

  if (!uptime) {
    return (
      <div className="card p-6 h-[300px] flex flex-col items-center justify-center">
        <div className="w-10 h-10 bg-surface-700 rounded-full flex items-center justify-center mb-3 border border-border">
          <svg className="w-5 h-5 text-content-tertiary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <p className="text-xs font-medium text-content-primary mb-1">No uptime data</p>
        <p className="text-[10px] text-content-tertiary">Wait for the monitoring service to record uptime.</p>
      </div>
    )
  }

  const percentage = uptime.uptime_percentage
  const radius = 56
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (percentage / 100) * circumference

  const getColor = () => {
    if (percentage >= 99) return '#10B981'
    if (percentage >= 95) return '#F59E0B'
    return '#EF4444'
  }

  return (
    <div className="card p-4 h-[300px] flex flex-col">
      <h3 className="text-sm font-medium text-content-primary mb-4">Uptime (Last 24h)</h3>
      <div className="flex-1 flex flex-col items-center justify-center">
        <div className="relative w-36 h-36">
          {/* Background circle */}
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="72"
              cy="72"
              r={radius}
              stroke="rgba(148, 163, 184, 0.1)"
              strokeWidth="10"
              fill="none"
            />
            {/* Progress circle */}
            <circle
              cx="72"
              cy="72"
              r={radius}
              stroke={getColor()}
              strokeWidth="10"
              fill="none"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              className="transition-all duration-700 ease-out"
            />
          </svg>
          {/* Inner text */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-2xl font-semibold font-mono-nums" style={{ color: getColor() }}>
              {percentage.toFixed(1)}%
            </span>
            <span className="text-[10px] font-medium text-content-tertiary uppercase tracking-wider mt-1">
              Uptime
            </span>
          </div>
        </div>

        {/* Footer Stats */}
        <div className="mt-6 flex items-center justify-center gap-6 w-full">
          <div className="text-center">
            <p className="text-[10px] font-medium text-content-tertiary uppercase tracking-wider mb-0.5">Checks</p>
            <p className="text-base font-semibold text-content-primary font-mono-nums">{uptime.total_checks}</p>
          </div>
          <div className="w-px h-6 bg-border"></div>
          <div className="text-center">
            <p className="text-[10px] font-medium text-content-tertiary uppercase tracking-wider mb-0.5">Success</p>
            <p className="text-base font-semibold text-success font-mono-nums">{uptime.successful_checks}</p>
          </div>
        </div>
      </div>
    </div>
  )
}


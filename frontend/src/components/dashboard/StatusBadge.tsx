interface StatusBadgeProps {
  status: 'success' | 'failure' | 'error' | 'timeout' | 'active' | 'inactive'
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const statusConfig = {
    success: { bg: 'bg-success-50', text: 'text-success-700', border: 'border-success-200/60', dot: 'bg-success-500' },
    failure: { bg: 'bg-danger-50', text: 'text-danger-700', border: 'border-danger-200/60', dot: 'bg-danger-500' },
    error: { bg: 'bg-danger-50', text: 'text-danger-700', border: 'border-danger-200/60', dot: 'bg-danger-500' },
    timeout: { bg: 'bg-warning-50', text: 'text-warning-700', border: 'border-warning-200/60', dot: 'bg-warning-500' },
    active: { bg: 'bg-success-50', text: 'text-success-700', border: 'border-success-200/60', dot: 'bg-success-500' },
    inactive: { bg: 'bg-zinc-100', text: 'text-zinc-700', border: 'border-zinc-200/80', dot: 'bg-zinc-400' },
  }

  const statusLabels = {
    success: 'Success',
    failure: 'Failure',
    error: 'Error',
    timeout: 'Timeout',
    active: 'Active',
    inactive: 'Inactive',
  }

  const config = statusConfig[status]

  return (
    <span className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${config.bg} ${config.text} border ${config.border} shadow-sm`}>
      <span className={`w-1.5 h-1.5 rounded-full ${config.dot} ${status === 'active' || status === 'success' ? 'animate-pulse' : ''}`}></span>
      <span>{statusLabels[status]}</span>
    </span>
  )
}

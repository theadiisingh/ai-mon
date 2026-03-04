export function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

export function formatDateTime(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatTime(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatDuration(ms: number): string {
  if (ms < 1000) {
    return `${ms}ms`
  } else if (ms < 60000) {
    return `${(ms / 1000).toFixed(2)}s`
  } else {
    const minutes = Math.floor(ms / 60000)
    const seconds = ((ms % 60000) / 1000).toFixed(0)
    return `${minutes}m ${seconds}s`
  }
}

export function formatPercentage(value: number | undefined | null, decimals: number = 2): string {
  if (value === undefined || value === null) return '0.00%'
  return `${value.toFixed(decimals)}%`
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US').format(value)
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str
  return str.slice(0, length) + '...'
}

export function getStatusColor(status: string): string {
  switch (status.toLowerCase()) {
    case 'success':
      return 'text-success bg-success/10 border-success/20'
    case 'failure':
    case 'error':
      return 'text-danger bg-danger/10 border-danger/20'
    case 'timeout':
      return 'text-warning bg-warning/10 border-warning/20'
    default:
      return 'text-content-tertiary bg-surface-600/20 border-surface-600/20'
  }
}

export function getMethodColor(method: string): string {
  switch (method.toUpperCase()) {
    case 'GET':
      return 'text-surface-300 bg-surface-700/50 border-border/30'
    case 'POST':
      return 'text-primary bg-primary/10 border-primary/20'
    case 'PUT':
      return 'text-warning bg-warning/10 border-warning/20'
    case 'DELETE':
      return 'text-danger bg-danger/10 border-danger/20'
    case 'PATCH':
      return 'text-accent bg-accent/10 border-accent/20'
    default:
      return 'text-surface-400 bg-surface-700/50 border-border/30'
  }
}

export function getUptimeColor(percentage: number): string {
  if (percentage >= 99) return 'text-success'
  if (percentage >= 95) return 'text-warning'
  return 'text-danger'
}

/**
 * Calculate average uptime from a list of API endpoints.
 * Uses the uptime_percentage field directly from the backend.
 */
export function calculateAverageUptime(endpoints: { uptime_percentage: number | null | undefined }[]): number {
  if (!endpoints || endpoints.length === 0) return 0
  
  const validEndpoints = endpoints.filter(ep => ep.uptime_percentage != null)
  if (validEndpoints.length === 0) return 0
  
  const total = validEndpoints.reduce((sum, ep) => sum + (ep.uptime_percentage || 0), 0)
  return total / validEndpoints.length
}

/**
 * Calculate uptime from raw check counts (as returned by metrics API).
 */
export function calculateUptimeFromCounts(successfulChecks: number, totalChecks: number): number {
  if (totalChecks === 0) return 100
  return (successfulChecks / totalChecks) * 100
}

/**
 * Get the appropriate uptime color based on percentage.
 * Returns 'success', 'warning', or 'danger' for use with StatCard.
 */
export function getUptimeStatus(percentage: number): 'success' | 'warning' | 'danger' {
  if (percentage >= 99) return 'success'
  if (percentage >= 95) return 'warning'
  return 'danger'
}

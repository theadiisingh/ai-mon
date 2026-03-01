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
      return 'text-green-600 bg-green-50'
    case 'failure':
    case 'error':
      return 'text-red-600 bg-red-50'
    case 'timeout':
      return 'text-yellow-600 bg-yellow-50'
    default:
      return 'text-gray-600 bg-gray-50'
  }
}

export function getMethodColor(method: string): string {
  switch (method.toUpperCase()) {
    case 'GET':
      return 'text-blue-600 bg-blue-50'
    case 'POST':
      return 'text-green-600 bg-green-50'
    case 'PUT':
      return 'text-orange-600 bg-orange-50'
    case 'DELETE':
      return 'text-red-600 bg-red-50'
    case 'PATCH':
      return 'text-purple-600 bg-purple-50'
    default:
      return 'text-gray-600 bg-gray-50'
  }
}

export function getUptimeColor(percentage: number): string {
  if (percentage >= 99) return 'text-green-600'
  if (percentage >= 95) return 'text-yellow-600'
  return 'text-red-600'
}

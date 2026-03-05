/**
 * Format a date string to local date display.
 * Handles ISO 8601 format with timezone info.
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

/**
 * Format a date/time string to local date/time display.
 * ALWAYS converts to local timezone by treating input as UTC.
 * This ensures consistent local time display regardless of backend timezone handling.
 */
export function formatDateTime(dateString: string): string {
  if (!dateString) return '-'
  
  // Handle different date formats
  let cleanDateString = dateString.trim()
  
  // If it has 'T', it's an ISO date - parse and convert to local
  if (cleanDateString.includes('T')) {
    // Split the date and time parts
    const parts = cleanDateString.split('T')
    const datePart = parts[0]
    let timePart = parts[1] || ''
    
    // Remove any timezone info (like +00:00, -05:30, Z)
    timePart = timePart.replace(/(\+\d{2}:\d{2}|-\d{2}:\d{2}|Z)$/, '')
    
    // Combine as UTC
    cleanDateString = `${datePart}T${timePart}Z`
  }
  
  const date = new Date(cleanDateString)
  
  // Check if the date is valid
  if (isNaN(date.getTime())) {
    return '-'
  }
  
  // Manually adjust for timezone if needed - treat as UTC and convert to local
  const utcDate = new Date(cleanDateString)
  
  // Format using local timezone - timezoneOffset is intentionally unused but kept for potential future use
  void date.getTimezoneOffset() // Preserve for potential timezone calculations
  
  return utcDate.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Format a time string to local time display.
 * Handles ISO 8601 format with timezone info.
 */
export function formatTime(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleTimeString(undefined, {
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

/**
 * Get uptime color class based on percentage.
 * Pure presentation function - no calculations.
 */
export function getUptimeColor(percentage: number): string {
  if (percentage >= 99) return 'text-success'
  if (percentage >= 95) return 'text-warning'
  return 'text-danger'
}

/**
 * Get the appropriate uptime status based on percentage.
 * Returns 'success', 'warning', or 'danger' for use with StatCard.
 * Pure presentation function - no calculations.
 */
export function getUptimeStatus(percentage: number): 'success' | 'warning' | 'danger' {
  if (percentage >= 99) return 'success'
  if (percentage >= 95) return 'warning'
  return 'danger'
}

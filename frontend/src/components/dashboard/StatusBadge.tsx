interface StatusBadgeProps {
  status: 'success' | 'failure' | 'error' | 'timeout' | 'active' | 'inactive'
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const statusClasses = {
    success: 'bg-success-100 text-success-700',
    failure: 'bg-danger-100 text-danger-700',
    error: 'bg-danger-100 text-danger-700',
    timeout: 'bg-warning-100 text-warning-700',
    active: 'bg-success-100 text-success-700',
    inactive: 'bg-gray-100 text-gray-700',
  }

  const statusLabels = {
    success: 'Success',
    failure: 'Failure',
    error: 'Error',
    timeout: 'Timeout',
    active: 'Active',
    inactive: 'Inactive',
  }

  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusClasses[status]}`}>
      {statusLabels[status]}
    </span>
  )
}

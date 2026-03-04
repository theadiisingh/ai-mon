import { motion } from 'framer-motion'

interface StatusBadgeProps {
  status: 'success' | 'failure' | 'error' | 'timeout' | 'active' | 'inactive'
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const statusConfig = {
    success: { 
      bg: 'bg-success/10', 
      text: 'text-success', 
      border: 'border-success/20', 
      dot: 'bg-success',
    },
    failure: { 
      bg: 'bg-danger/10', 
      text: 'text-danger', 
      border: 'border-danger/20', 
      dot: 'bg-danger',
    },
    error: { 
      bg: 'bg-danger/10', 
      text: 'text-danger', 
      border: 'border-danger/20', 
      dot: 'bg-danger',
    },
    timeout: { 
      bg: 'bg-warning/10', 
      text: 'text-warning', 
      border: 'border-warning/20', 
      dot: 'bg-warning',
    },
    active: { 
      bg: 'bg-success/10', 
      text: 'text-success', 
      border: 'border-success/20', 
      dot: 'bg-success',
    },
    inactive: { 
      bg: 'bg-surface-600/20', 
      text: 'text-surface-400', 
      border: 'border-surface-600/20', 
      dot: 'bg-surface-500',
    },
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
  const isPulsing = status === 'active' || status === 'success'

  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium ${config.bg} ${config.text} border ${config.border}`}>
      <motion.span 
        className={`w-1.5 h-1.5 rounded-full ${config.dot}`}
        animate={isPulsing ? {
          scale: [1, 1.2, 1],
          opacity: [1, 0.7, 1],
        } : {}}
        transition={isPulsing ? {
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut"
        } : {}}
      />
      <span>{statusLabels[status]}</span>
    </span>
  )
}


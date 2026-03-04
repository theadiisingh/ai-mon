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
      dotGlow: 'shadow-[0_0_6px_rgba(16,185,129,0.4)]',
    },
    failure: { 
      bg: 'bg-danger/10', 
      text: 'text-danger', 
      border: 'border-danger/20', 
      dot: 'bg-danger',
      dotGlow: 'shadow-[0_0_6px_rgba(220,38,38,0.4)]',
    },
    error: { 
      bg: 'bg-danger/10', 
      text: 'text-danger', 
      border: 'border-danger/20', 
      dot: 'bg-danger',
      dotGlow: 'shadow-[0_0_6px_rgba(220,38,38,0.4)]',
    },
    timeout: { 
      bg: 'bg-warning/10', 
      text: 'text-warning', 
      border: 'border-warning/20', 
      dot: 'bg-warning',
      dotGlow: 'shadow-[0_0_6px_rgba(217,119,6,0.4)]',
    },
    active: { 
      bg: 'bg-success/10', 
      text: 'text-success', 
      border: 'border-success/20', 
      dot: 'bg-success',
      dotGlow: 'shadow-[0_0_6px_rgba(16,185,129,0.4)]',
    },
    inactive: { 
      bg: 'bg-surface-600/20', 
      text: 'text-content-tertiary', 
      border: 'border-surface-600/20', 
      dot: 'bg-surface-500',
      dotGlow: '',
    },
  }

  const statusLabels = {
    success: 'Healthy',
    failure: 'Failed',
    error: 'Error',
    timeout: 'Timeout',
    active: 'Active',
    inactive: 'Inactive',
  }

  const config = statusConfig[status]
  const isActive = status === 'active' || status === 'success'

  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium ${config.bg} ${config.text} border ${config.border}`}>
      <motion.span 
        className={`w-1.5 h-1.5 rounded-full ${config.dot} ${config.dotGlow}`}
        animate={isActive ? {
          scale: [1, 1.1, 1],
        } : {}}
        transition={isActive ? {
          duration: 2,
          repeat: Infinity,
          ease: "linear"
        } : {}}
      />
      <span>{statusLabels[status]}</span>
    </span>
  )
}


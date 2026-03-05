
import { motion } from 'framer-motion';

type StatusType = 'success' | 'failure' | 'error' | 'timeout' | 'active' | 'inactive' | 'up' | 'down' | 'unknown' | 'checking'

interface StatusConfig {
  bg: string;
  text: string;
  border: string;
  dot: string;
  dotGlow: string;
  label: string;
  animate?: boolean;
}

interface StatusBadgeProps {
  status: StatusType
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const statusConfig: Record<StatusType, StatusConfig> = {
    success: { 
      bg: 'bg-emerald-500/5', 
      text: 'text-emerald-400', 
      border: 'border-emerald-500/10', 
      dot: 'bg-emerald-400',
      dotGlow: 'shadow-[0_0_4px_rgba(52,211,153,0.3)]',
      label: 'Healthy',
    },
    up: { 
      bg: 'bg-emerald-500/5', 
      text: 'text-emerald-400', 
      border: 'border-emerald-500/10', 
      dot: 'bg-emerald-400',
      dotGlow: 'shadow-[0_0_4px_rgba(52,211,153,0.3)]',
      label: 'UP',
    },
    failure: { 
      bg: 'bg-red-500/5', 
      text: 'text-red-400', 
      border: 'border-red-500/10', 
      dot: 'bg-red-400',
      dotGlow: 'shadow-[0_0_4px_rgba(248,113,113,0.3)]',
      label: 'Failed',
    },
    down: { 
      bg: 'bg-red-500/5', 
      text: 'text-red-400', 
      border: 'border-red-500/10', 
      dot: 'bg-red-400',
      dotGlow: 'shadow-[0_0_4px_rgba(248,113,113,0.3)]',
      label: 'DOWN',
    },
    error: { 
      bg: 'bg-red-500/5', 
      text: 'text-red-400', 
      border: 'border-red-500/10', 
      dot: 'bg-red-400',
      dotGlow: 'shadow-[0_0_4px_rgba(248,113,113,0.3)]',
      label: 'Error',
    },
    timeout: { 
      bg: 'bg-amber-500/5', 
      text: 'text-amber-400', 
      border: 'border-amber-500/10', 
      dot: 'bg-amber-400',
      dotGlow: 'shadow-[0_0_4px_rgba(251,191,36,0.3)]',
      label: 'Timeout',
    },
    active: { 
      bg: 'bg-emerald-500/5', 
      text: 'text-emerald-400', 
      border: 'border-emerald-500/10', 
      dot: 'bg-emerald-400',
      dotGlow: 'shadow-[0_0_4px_rgba(52,211,153,0.3)]',
      label: 'Active',
    },
    checking: { 
      bg: 'bg-blue-500/5', 
      text: 'text-blue-400', 
      border: 'border-blue-500/10', 
      dot: 'bg-blue-400',
      dotGlow: 'shadow-[0_0_4px_rgba(96,165,250,0.3)]',
      label: 'Checking',
      animate: true,
    },
    inactive: { 
      bg: 'bg-slate-500/5', 
      text: 'text-slate-400', 
      border: 'border-slate-500/10', 
      dot: 'bg-slate-400',
      dotGlow: '',
      label: 'Inactive',
    },
    unknown: { 
      bg: 'bg-slate-500/5', 
      text: 'text-slate-400', 
      border: 'border-slate-500/10', 
      dot: 'bg-slate-400',
      dotGlow: '',
      label: 'Unknown',
    },
  }

  const config = statusConfig[status]
  const isHealthy = status === 'up' || status === 'success' || status === 'active'
  const shouldAnimate = config.animate || isHealthy

  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium ${config.bg} ${config.text} border ${config.border}`}>
      <motion.span 
        className={`w-1.5 h-1.5 rounded-full ${config.dot} ${config.dotGlow}`}
        animate={shouldAnimate ? {
          scale: [1, 1.2, 1],
          opacity: [1, 0.7, 1],
        } : {}}
        transition={config.animate ? {
          duration: 1,
          repeat: Infinity,
          ease: "easeInOut"
        } : isHealthy ? {
          duration: 2,
          repeat: Infinity,
          ease: "linear"
        } : {}}
      />
      <span>{config.label}</span>
    </span>
  )
}


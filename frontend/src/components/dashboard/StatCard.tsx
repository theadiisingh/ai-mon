import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'

interface StatCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon?: React.ReactNode
  trend?: {
    value: number
    isPositive: boolean
  }
  color?: 'primary' | 'success' | 'warning' | 'danger'
}

export default function StatCard({ title, value, subtitle, icon, trend, color = 'primary' }: StatCardProps) {
  const [displayValue, setDisplayValue] = useState<string | number>(0)
  
  const colorConfig = {
    primary: {
      accent: 'text-primary',
      iconBg: 'bg-primary/10 backdrop-blur-sm border border-primary/10',
      glow: 'group-hover:shadow-primary/5',
    },
    success: {
      accent: 'text-emerald-500',
      iconBg: 'bg-emerald-500/10 backdrop-blur-sm border border-emerald-500/10',
      glow: 'group-hover:shadow-emerald-500/5',
    },
    warning: {
      accent: 'text-amber-500',
      iconBg: 'bg-amber-500/10 backdrop-blur-sm border border-amber-500/10',
      glow: 'group-hover:shadow-amber-500/5',
    },
    danger: {
      accent: 'text-red-500',
      iconBg: 'bg-red-500/10 backdrop-blur-sm border border-red-500/10',
      glow: 'group-hover:shadow-red-500/5',
    },
  }

  const config = colorConfig[color]

  // Subtle number animation
  useEffect(() => {
    const numValue = typeof value === 'number' ? value : parseFloat(String(value).replace(/[^0-9.-]/g, '')) || 0
    if (!isNaN(numValue) && typeof value === 'number') {
      const duration = 800
      const steps = 20
      const increment = numValue / steps
      let current = 0
      
      const timer = setInterval(() => {
        current += increment
        if (current >= numValue) {
          setDisplayValue(value)
          clearInterval(timer)
        } else {
          setDisplayValue(Math.floor(current))
        }
      }, duration / steps)
      
      return () => clearInterval(timer)
    } else {
      setDisplayValue(value)
    }
  }, [value])

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
      whileHover={{ y: -2, transition: { duration: 0.15 } }}
      className={`card card-hover p-4 flex flex-col justify-between group bg-surface-800/40 backdrop-blur-sm ${config.glow}`}
      style={{
        boxShadow: '0 4px 24px rgba(0, 0, 0, 0.15), 0 1px 2px rgba(0, 0, 0, 0.1)',
      }}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-2xs font-medium text-content-tertiary uppercase tracking-wider">{title}</p>
          <div className="flex items-baseline gap-2 mt-1.5">
            <h3 className="text-2xl font-semibold text-content-primary font-mono-nums tracking-tight">
              {typeof value === 'number' ? displayValue : value}
            </h3>
            {trend && (
              <p className={`text-xs font-medium font-mono-nums ${trend.isPositive ? 'text-emerald-500' : 'text-red-500'}`}>
                {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
              </p>
            )}
          </div>
          {subtitle && (
            <p className="text-xs text-content-tertiary mt-1.5">{subtitle}</p>
          )}
        </div>
        {icon && (
          <div className={`p-2.5 rounded-md ${config.iconBg}`}>
            <span className={config.accent}>{icon}</span>
          </div>
        )}
      </div>
    </motion.div>
  )
}


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
      iconBg: 'bg-surface-700',
    },
    success: {
      accent: 'text-success',
      iconBg: 'bg-surface-700',
    },
    warning: {
      accent: 'text-warning',
      iconBg: 'bg-surface-700',
    },
    danger: {
      accent: 'text-danger',
      iconBg: 'bg-surface-700',
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
      className="card p-4 flex flex-col justify-between"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-[11px] font-medium text-content-tertiary uppercase tracking-wide">{title}</p>
          <div className="flex items-baseline gap-2 mt-1.5">
            <h3 className="text-2xl font-semibold text-content-primary font-mono-nums">
              {typeof value === 'number' ? displayValue : value}
            </h3>
            {trend && (
              <p className={`text-xs font-medium ${trend.isPositive ? 'text-success' : 'text-danger'}`}>
                {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
              </p>
            )}
          </div>
          {subtitle && (
            <p className="text-xs text-content-tertiary mt-1">{subtitle}</p>
          )}
        </div>
        {icon && (
          <div className={`p-2 rounded-md ${config.iconBg}`}>
            <span className={config.accent}>{icon}</span>
          </div>
        )}
      </div>
    </motion.div>
  )
}


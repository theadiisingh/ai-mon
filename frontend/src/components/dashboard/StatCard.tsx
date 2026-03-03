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
  const colorClasses = {
    primary: 'bg-primary-50 text-primary-600 shadow-primary-100',
    success: 'bg-success-50 text-success-600 shadow-success-100',
    warning: 'bg-warning-50 text-warning-600 shadow-warning-100',
    danger: 'bg-danger-50 text-danger-600 shadow-danger-100',
  }

  return (
    <div className="card p-6 flex flex-col justify-center relative overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-floating">
      <div className="flex items-start justify-between">
        <div className="z-10">
          <p className="text-sm font-medium text-zinc-500 tracking-wide">{title}</p>
          <div className="flex items-baseline space-x-2 mt-2">
            <h3 className="text-3xl font-bold text-zinc-900 tracking-tight">{value}</h3>
            {trend && (
              <p className={`text-sm font-semibold flex items-center ${trend.isPositive ? 'text-success-600' : 'text-danger-600'}`}>
                {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
              </p>
            )}
          </div>
          {subtitle && (
            <p className="text-sm text-zinc-500 mt-2">{subtitle}</p>
          )}
        </div>
        {icon && (
          <div className={`p-3 rounded-xl shadow-sm z-10 ${colorClasses[color]}`}>
            {icon}
          </div>
        )}
      </div>
      {/* Decorative background blur */}
      <div className={`absolute -right-4 -bottom-4 w-24 h-24 rounded-full opacity-20 blur-2xl ${colorClasses[color].split(' ')[0]}`}></div>
    </div>
  )
}

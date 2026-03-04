import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, PlusCircle, Activity, Shield } from 'lucide-react'

export default function Sidebar() {
  const location = useLocation()

  const navItems = [
    {
      path: '/dashboard',
      label: 'Dashboard',
      icon: <LayoutDashboard className="w-4 h-4" />
    },
    {
      path: '/apis/new',
      label: 'Add API',
      icon: <PlusCircle className="w-4 h-4" />
    },
  ]

  return (
    <aside className="w-60 h-screen bg-surface-900 border-r border-border flex flex-col shrink-0">
      {/* Logo */}
      <div className="px-4 py-5 border-b border-border">
        <Link to="/dashboard" className="flex items-center gap-3 group">
          <div className="w-8 h-8 bg-surface-700 rounded-md flex items-center justify-center">
            <Shield className="w-4 h-4 text-content-secondary" />
          </div>
          <div>
            <span className="text-sm font-semibold text-content-primary tracking-tight">AI MON</span>
            <p className="text-[10px] text-content-tertiary tracking-wide uppercase">Intelligence</p>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="px-3 py-4 flex-1">
        <div className="text-[11px] font-medium text-content-tertiary uppercase tracking-wider mb-3 px-2">Operations</div>
        {navItems.map((item) => {
          const isActive = location.pathname === item.path
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-2.5 px-2.5 py-2 rounded-md text-sm font-medium transition-colors duration-150 relative ${
                isActive
                  ? 'text-content-primary bg-surface-700'
                  : 'text-content-secondary hover:text-content-primary hover:bg-surface-800'
              }`}
            >
              {/* Active indicator - thin vertical line */}
              {isActive && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-4 bg-primary rounded-r" />
              )}
              <span className={isActive ? 'text-primary' : 'text-content-tertiary'}>
                {item.icon}
              </span>
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>

      {/* Status footer */}
      <div className="px-3 py-3 border-t border-border">
        <div className="flex items-center gap-2 px-2">
          <div className="w-6 h-6 rounded bg-surface-700 flex items-center justify-center">
            <Activity className="w-3 h-3 text-content-tertiary" />
          </div>
          <div className="text-xs">
            <p className="font-medium text-content-secondary">System Operational</p>
          </div>
        </div>
      </div>
    </aside>
  )
}


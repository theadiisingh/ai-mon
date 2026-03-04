import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, PlusCircle, Shield, BarChart3 } from 'lucide-react'

export default function Sidebar() {
  const location = useLocation()

  const navItems = [
    {
      path: '/dashboard',
      label: 'Overview',
      icon: <LayoutDashboard className="w-4 h-4" />
    },
    {
      path: '/apis/new',
      label: 'Add Endpoint',
      icon: <PlusCircle className="w-4 h-4" />
    },
  ]

  return (
    <aside className="w-56 h-screen bg-surface-900/40 backdrop-blur-xl border-r border-white/5 flex flex-col shrink-0 relative">
      {/* Vertical accent line - brand signature */}
      <div className="absolute left-0 top-0 bottom-0 w-px bg-gradient-to-b from-accent/60 via-accent/30 to-transparent" />
      
      {/* Logo */}
      <div className="px-4 py-5 border-b border-white/5">
        <Link to="/dashboard" className="flex items-center gap-3 group">
          <div className="w-8 h-8 bg-surface-800/50 backdrop-blur-sm border border-white/5 rounded flex items-center justify-center">
            <Shield className="w-4 h-4 text-accent-light" />
          </div>
          <div>
            <span className="text-sm font-semibold text-content-primary tracking-tight">AIMON</span>
            <p className="text-[10px] text-content-tertiary tracking-wider uppercase">Intelligence</p>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="px-3 py-4 flex-1">
        <div className="text-[10px] font-medium text-content-tertiary uppercase tracking-widest mb-3 px-2">Operations</div>
        {navItems.map((item) => {
          const isActive = location.pathname === item.path
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`sidebar-link relative mb-0.5 ${isActive ? 'active' : ''}`}
            >
              {/* Active indicator */}
              {isActive && <div className="nav-indicator" />}
              <span className={isActive ? 'text-accent-light' : 'text-content-tertiary group-hover:text-content-secondary'}>
                {item.icon}
              </span>
              <span>{item.label}</span>
            </Link>
          )
        })}
        
        {/* Secondary section */}
        <div className="text-[10px] font-medium text-content-tertiary uppercase tracking-widest mt-6 mb-3 px-2">Insights</div>
        <Link
          to="/dashboard"
          className="sidebar-link relative mb-0.5"
        >
          <span className="text-content-tertiary">
            <BarChart3 className="w-4 h-4" />
          </span>
          <span>Analytics</span>
        </Link>
      </nav>

      {/* Status footer */}
      <div className="px-3 py-3 border-t border-white/5">
        <div className="flex items-center gap-2.5 px-2 py-1.5 bg-surface-800/40 backdrop-blur-sm rounded border border-white/5">
          <div className="relative">
            <div className="w-2 h-2 rounded-full bg-success"></div>
            <div className="absolute inset-0 w-2 h-2 rounded-full bg-success animate-ping opacity-50"></div>
          </div>
          <div className="text-xs">
            <p className="font-medium text-content-secondary">System Active</p>
            <p className="text-[10px] text-content-tertiary">All services operational</p>
          </div>
        </div>
      </div>
    </aside>
  )
}


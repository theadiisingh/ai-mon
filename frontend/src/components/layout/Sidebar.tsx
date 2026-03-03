import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, PlusCircle, Activity } from 'lucide-react'

export default function Sidebar() {
  const location = useLocation()

  const navItems = [
    {
      path: '/dashboard',
      label: 'Dashboard',
      icon: <LayoutDashboard className="w-5 h-5" />
    },
    {
      path: '/apis/new',
      label: 'Add API',
      icon: <PlusCircle className="w-5 h-5" />
    },
  ]

  return (
    <aside className="w-64 bg-zinc-50 border-r border-zinc-200/80 min-h-screen flex flex-col transition-all">
      <div className="p-6">
        <Link to="/dashboard" className="flex items-center space-x-3 group">
          <div className="w-9 h-9 bg-primary-600 rounded-xl flex items-center justify-center shadow-sm group-hover:bg-primary-500 transition-colors">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <span className="text-lg font-bold text-zinc-900 tracking-tight">AI MON</span>
        </Link>
      </div>

      <nav className="px-4 space-y-1 mt-2 flex-1">
        <div className="text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-4 px-3">Menu</div>
        {navItems.map((item) => {
          const isActive = location.pathname === item.path
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all duration-200 text-sm font-medium ${isActive
                  ? 'bg-white text-zinc-900 shadow-sm ring-1 ring-zinc-200/50'
                  : 'text-zinc-500 hover:bg-zinc-100 hover:text-zinc-900'
                }`}
            >
              <div className={`${isActive ? 'text-primary-600' : 'text-zinc-400'}`}>
                {item.icon}
              </div>
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>

      <div className="p-4 m-4 bg-white rounded-xl border border-zinc-200/60 shadow-sm">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-zinc-100 to-zinc-50 border border-zinc-200 flex items-center justify-center">
            <Activity className="w-4 h-4 text-zinc-500" />
          </div>
          <div className="text-xs">
            <p className="font-semibold text-zinc-900">AI MON v1.0.0</p>
            <p className="text-zinc-500">Smart API Monitoring</p>
          </div>
        </div>
      </div>
    </aside>
  )
}

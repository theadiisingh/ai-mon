import { useAuth } from '../../hooks/useAuth'
import { Bell, Search, LogOut, User } from 'lucide-react'

export default function Navbar() {
  const { user, logout } = useAuth()

  return (
    <header className="sticky top-0 z-20 h-14">
      {/* Floating glass bar */}
      <div className="absolute inset-x-0 h-full bg-[#11161D]/70 backdrop-blur-xl border-b border-white/5 shadow-lg shadow-black/10" />
      
      <div className="relative flex items-center justify-between h-full px-5">
        <div className="flex items-center gap-4 flex-1">
          {/* Minimal search bar */}
          <div className="hidden md:flex items-center relative w-64">
            <Search className="w-3.5 h-3.5 text-content-tertiary absolute left-2.5" />
            <input
              type="text"
              placeholder="Search endpoints..."
              className="w-full pl-8 pr-3 py-1.5 text-xs bg-surface-800/30 backdrop-blur-sm border border-white/5 rounded text-content-primary placeholder:text-content-tertiary focus:bg-surface-700/50 focus:border-primary/30 focus:outline-none transition-all duration-150"
            />
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Notifications - minimal */}
          <button className="text-content-tertiary hover:text-content-secondary transition-colors duration-150 p-1.5 rounded hover:bg-white/5">
            <Bell className="w-4 h-4" />
          </button>

          <div className="h-4 w-px bg-white/10"></div>

          {/* User Profile */}
          <div className="flex items-center gap-2.5">
            <div className="text-xs text-right hidden sm:block">
              <p className="font-medium text-content-primary leading-tight">{user?.username}</p>
              <p className="text-content-tertiary text-[10px]">{user?.email}</p>
            </div>
            <div className="w-7 h-7 bg-gradient-to-br from-primary/20 to-primary/5 backdrop-blur-sm border border-primary/10 rounded flex items-center justify-center">
              <User className="w-3.5 h-3.5 text-primary" />
            </div>
          </div>

          {/* Logout */}
          <button
            onClick={logout}
            className="text-xs font-medium text-content-tertiary hover:text-content-secondary transition-colors duration-150 p-1.5 rounded hover:bg-white/5"
            title="Logout"
          >
            <LogOut className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </header>
  )
}


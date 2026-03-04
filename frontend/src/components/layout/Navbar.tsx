import { useAuth } from '../../hooks/useAuth'
import { Bell, Search, LogOut, User } from 'lucide-react'

export default function Navbar() {
  const { user, logout } = useAuth()

  return (
    <header className="sticky top-0 z-20 h-14 border-b border-border bg-surface-900/80 backdrop-blur-sm">
      <div className="flex items-center justify-between h-full px-6">
        <div className="flex items-center gap-4 flex-1">
          {/* Minimal search bar */}
          <div className="hidden md:flex items-center relative w-72">
            <Search className="w-3.5 h-3.5 text-content-tertiary absolute left-3" />
            <input
              type="text"
              placeholder="Search..."
              className="w-full pl-9 pr-3 py-1.5 text-xs bg-surface-800 border border-border rounded-md text-content-primary placeholder:text-content-tertiary focus:bg-surface-700 focus:border-primary/50 focus:outline-none transition-colors"
            />
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Notifications - minimal */}
          <button className="text-content-tertiary hover:text-content-secondary transition-colors p-1.5 rounded hover:bg-surface-800">
            <Bell className="w-4 h-4" />
          </button>

          <div className="h-4 w-px bg-border"></div>

          {/* User Profile */}
          <div className="flex items-center gap-2.5">
            <div className="text-xs text-right hidden sm:block">
              <p className="font-medium text-content-primary leading-tight">{user?.username}</p>
              <p className="text-content-tertiary text-[10px]">{user?.email}</p>
            </div>
            <div className="w-7 h-7 bg-surface-700 rounded-md flex items-center justify-center">
              <User className="w-3.5 h-3.5 text-content-secondary" />
            </div>
          </div>

          {/* Logout */}
          <button
            onClick={logout}
            className="text-xs font-medium text-content-tertiary hover:text-content-secondary transition-colors p-1.5 rounded hover:bg-surface-800"
            title="Logout"
          >
            <LogOut className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </header>
  )
}


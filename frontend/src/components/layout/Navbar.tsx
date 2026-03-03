import { useAuth } from '../../hooks/useAuth'
import { Bell, Search } from 'lucide-react'

export default function Navbar() {
  const { user, logout } = useAuth()

  return (
    <header className="sticky top-0 z-30 bg-white/80 backdrop-blur-md border-b border-zinc-200/80 transition-all duration-200">
      <div className="flex items-center justify-between px-6 py-3 md:px-8">
        <div className="flex items-center space-x-4 flex-1">
          {/* Optional Search Bar Placeholder for SaaS Feel */}
          <div className="hidden md:flex items-center relative w-64">
            <Search className="w-4 h-4 text-zinc-400 absolute left-3" />
            <input
              type="text"
              placeholder="Search..."
              className="w-full pl-9 pr-4 py-1.5 text-sm bg-zinc-100/50 border-transparent rounded-lg focus:bg-white focus:border-zinc-300 focus:ring-2 focus:ring-primary-500/20 outline-none transition-all placeholder:text-zinc-500"
            />
          </div>
        </div>

        <div className="flex items-center space-x-5">
          <button className="text-zinc-400 hover:text-zinc-600 transition-colors relative">
            <Bell className="w-5 h-5" />
            <span className="absolute top-0 right-0 w-2 h-2 bg-primary-500 rounded-full border-2 border-white"></span>
          </button>

          <div className="h-6 w-px bg-zinc-200"></div>

          <div className="flex items-center space-x-3">
            <div className="text-sm text-right hidden sm:block">
              <p className="font-semibold text-zinc-900 leading-tight">{user?.username}</p>
              <p className="text-zinc-500 text-xs">{user?.email}</p>
            </div>
            <div className="w-9 h-9 bg-gradient-to-tr from-primary-100 to-primary-50 border border-primary-200 rounded-full flex items-center justify-center shadow-sm">
              <span className="text-sm font-semibold text-primary-700">
                {user?.username?.charAt(0).toUpperCase() || 'U'}
              </span>
            </div>
          </div>

          <button
            onClick={logout}
            className="text-sm font-medium text-zinc-500 hover:text-zinc-900 transition-colors ml-2"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  )
}

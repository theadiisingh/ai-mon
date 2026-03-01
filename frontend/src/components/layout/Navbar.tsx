import { useAuth } from '../../hooks/useAuth'

export default function Navbar() {
  const { user, logout } = useAuth()

  return (
    <header className="bg-white border-b border-gray-200">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center space-x-4">
          <h2 className="text-xl font-semibold text-gray-900">
            Dashboard
          </h2>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-primary-600">
                {user?.username?.charAt(0).toUpperCase() || 'U'}
              </span>
            </div>
            <div className="text-sm">
              <p className="font-medium text-gray-900">{user?.username}</p>
              <p className="text-gray-500 text-xs">{user?.email}</p>
            </div>
          </div>

          <button
            onClick={logout}
            className="btn btn-secondary text-sm"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  )
}

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { User } from '../types/user'
import { authApi } from '../api/authApi'

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, username: string, password: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check for token on mount
    const token = localStorage.getItem('access_token')
    if (token) {
      // Validate token and get user
      authApi.me()
        .then((response) => {
          setUser(response.data)
        })
        .catch(() => {
          // Token invalid, clear it but don't redirect immediately
          localStorage.removeItem('access_token')
        })
        .finally(() => {
          setLoading(false)
        })
    } else {
      setLoading(false)
    }
  }, [])

  const refreshUser = async () => {
    try {
      const response = await authApi.me()
      setUser(response.data)
    } catch (error) {
      console.error('Failed to refresh user:', error)
    }
  }

  const login = async (email: string, password: string) => {
    const response = await authApi.login(email, password)
    const { access_token } = response.data
    localStorage.setItem('access_token', access_token)
    const userResponse = await authApi.me()
    setUser(userResponse.data)
  }

  const register = async (email: string, username: string, password: string) => {
    await authApi.register({ email, username, password })
    await login(email, password)
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        loading,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

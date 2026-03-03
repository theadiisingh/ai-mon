import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { AxiosResponse } from 'axios'
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

// Lock to prevent multiple simultaneous token refresh operations
let isRefreshing = false
let refreshPromise: Promise<boolean> | null = null

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  // Helper function to handle token refresh with locking
  const handleTokenRefresh = async (): Promise<boolean> => {
    // If already refreshing, wait for it to complete
    if (isRefreshing && refreshPromise) {
      return refreshPromise
    }

    isRefreshing = true
    refreshPromise = (async (): Promise<boolean> => {
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (!refreshToken) {
          throw new Error('No refresh token')
        }

        const response: AxiosResponse<{ access_token: string; refresh_token?: string }> = 
          await authApi.refreshToken()
        
        if (response.data) {
          const { access_token, refresh_token } = response.data
          localStorage.setItem('access_token', access_token)
          if (refresh_token) {
            localStorage.setItem('refresh_token', refresh_token)
          }
          return true
        }
        return false
      } catch (error) {
        // Refresh failed - clear tokens
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        return false
      } finally {
        isRefreshing = false
        refreshPromise = null
      }
    })()

    return refreshPromise
  }

  useEffect(() => {
    // Check for token on mount
    const initializeAuth = async () => {
      const token = localStorage.getItem('access_token')
      
      if (token) {
        try {
          // Validate token and get user
          const response: AxiosResponse<User> = await authApi.me()
          if (response.data) {
            setUser(response.data)
          }
        } catch {
          // Token invalid, try refresh token
          const refreshSuccess = await handleTokenRefresh()
          if (!refreshSuccess) {
            localStorage.removeItem('access_token')
          }
        }
      } else {
        // No access token, check for refresh token
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const refreshSuccess = await handleTokenRefresh()
          if (refreshSuccess) {
            try {
              const userResponse: AxiosResponse<User> = await authApi.me()
              if (userResponse.data) {
                setUser(userResponse.data)
              }
            } catch {
              // Token refresh worked but user fetch failed
              localStorage.removeItem('access_token')
              localStorage.removeItem('refresh_token')
            }
          }
        }
      }
      
      setLoading(false)
    }

    initializeAuth()
  }, [])

  const refreshUser = async () => {
    try {
      const response: AxiosResponse<User> = await authApi.me()
      if (response.data) {
        setUser(response.data)
      }
    } catch (error) {
      console.error('Failed to refresh user:', error)
      // Try to refresh the token
      const refreshSuccess = await handleTokenRefresh()
      if (refreshSuccess) {
        try {
          const userResponse: AxiosResponse<User> = await authApi.me()
          if (userResponse.data) {
            setUser(userResponse.data)
          }
        } catch {
          // Refresh worked but user fetch failed
          logout()
        }
      } else {
        // Refresh failed, logout
        logout()
      }
    }
  }

  const login = async (email: string, password: string) => {
    console.log('[Auth] Starting login for:', email)
    
    try {
      // First, login to get tokens
      const response: AxiosResponse<{ access_token: string; refresh_token?: string }> = await authApi.login(email, password)
      console.log('[Auth] Login response received:', response.data)
      
      const tokenData = response.data
      const access_token = tokenData?.access_token
      const refresh_token = tokenData?.refresh_token
      
      if (!access_token) {
        throw new Error('Login failed: No access token received')
      }
      
      // Store tokens FIRST
      localStorage.setItem('access_token', access_token)
      if (refresh_token) {
        localStorage.setItem('refresh_token', refresh_token)
      }
      console.log('[Auth] Tokens stored in localStorage')
      
      // Small delay to ensure token is stored and axios interceptor picks it up
      await new Promise(resolve => setTimeout(resolve, 50))
      
      // Then get user info - this MUST succeed for login to work properly
      const userResponse: AxiosResponse<User> = await authApi.me()
      console.log('[Auth] User data received:', userResponse.data)
      
      if (userResponse.data) {
        setUser(userResponse.data)
        console.log('[Auth] User set successfully')
      } else {
        throw new Error('Login failed: Could not get user data')
      }
    } catch (error: any) {
      console.error('[Auth] Login error:', error)
      // Clear any partial state
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      
      // Re-throw with more specific error message
      if (error.response?.status === 401) {
        throw new Error('Invalid email or password')
      } else if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail)
      } else if (error.message) {
        throw new Error(error.message)
      } else {
        throw new Error('Login failed. Please try again.')
      }
    }
  }

  const register = async (email: string, username: string, password: string) => {
    console.log('[Auth] Starting registration for:', email)
    
    try {
      // Register now returns tokens directly in the response
      const response = await authApi.register({ email, username, password })
      const { access_token, refresh_token, user } = response.data
      
      // Store tokens
      localStorage.setItem('access_token', access_token)
      if (refresh_token) {
        localStorage.setItem('refresh_token', refresh_token)
      }
      console.log('[Auth] Registration successful, user set')
      
      // Set user
      setUser(user)
    } catch (error: any) {
      console.error('[Auth] Registration error:', error)
      // Clear any partial state
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      
      // Re-throw with more specific error message
      if (error.response?.status === 400) {
        throw new Error(error.response?.data?.detail || 'Registration failed. Email may already be in use.')
      } else if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail)
      } else if (error.message) {
        throw new Error(error.message)
      } else {
        throw new Error('Registration failed. Please try again.')
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
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

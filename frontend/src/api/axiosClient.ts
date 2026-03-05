import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'

// CRITICAL: ALWAYS use /api prefix - Vite proxy forwards to backend at localhost:8000
// NEVER use import.meta.env.VITE_API_URL - it bypasses the proxy and causes CORS issues
// The proxy is required for proper CORS handling with Authorization headers
const API_BASE_URL = '/api'

// Create axios instance with proxy base URL
const axiosClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
  withCredentials: false,
})

// Create a separate axios instance for token refresh to avoid interceptor loops
// Use same base URL to ensure consistency
const refreshAxios = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  timeout: 30000,
})

// Auth routes that should NOT have tokens attached
const AUTH_ROUTES = ['/auth/login', '/auth/register', '/auth/refresh']

// Helper to check if a URL is an auth route
const isAuthRoute = (url: string): boolean => {
  return AUTH_ROUTES.some(route => url?.includes(route))
}

// Request interceptor to add auth token
axiosClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const url = config.url || ''
    
    // Skip token for auth routes
    if (isAuthRoute(url)) {
      return config
    }
    
    // If this request already has Authorization header set (from retry), use it
    if (config.headers?.Authorization) {
      return config
    }
    
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Track refresh token attempts to prevent infinite loops
let isRefreshing = false

// Response interceptor to handle errors and token refresh
axiosClient.interceptors.response.use(
  (response) => {
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
    const url = originalRequest?.url || 'unknown'
    
    // Handle 401 Unauthorized - only for non-auth routes
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry && !isAuthRoute(url)) {
      // Prevent multiple simultaneous refresh attempts
      if (isRefreshing) {
        return Promise.reject(error)
      }
      
      originalRequest._retry = true
      isRefreshing = true
      
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        
        if (!refreshToken) {
          // No refresh token - force logout
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
          return Promise.reject(error)
        }
        
        // Use separate axios instance for refresh to avoid interceptor issues
        const formData = new URLSearchParams()
        formData.append('grant_type', 'refresh_token')
        
        const response = await refreshAxios.post(
          '/auth/refresh',
          formData,
          {
            headers: {
              'Authorization': `Bearer ${refreshToken}`,
            },
          }
        )
        
        const { access_token, refresh_token: newRefreshToken } = response.data
        
        if (!access_token) {
          throw new Error('No access token in refresh response')
        }
        
        // Store new tokens
        localStorage.setItem('access_token', access_token)
        if (newRefreshToken) {
          localStorage.setItem('refresh_token', newRefreshToken)
        }
        
        // Retry the original request with new token
        // The interceptor will pick up the new token from localStorage
        // because we check for existing Authorization header first
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`
        }
        
        isRefreshing = false
        return axiosClient(originalRequest)
      } catch (refreshError) {
        isRefreshing = false
        
        // Clear tokens and trigger logout on refresh failure
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        
        // Only redirect if we're not already on login page
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login'
        }
        
        return Promise.reject(refreshError)
      }
    }
    
    return Promise.reject(error)
  }
)

export default axiosClient

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
      console.log('[API] Skipping token for auth route:', url)
      return config
    }
    
    // If this request already has Authorization header set (from retry), use it
    if (config.headers?.Authorization) {
      console.log('[API] ➤ Request to:', url, '| Using pre-set token')
      return config
    }
    
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
      // Debug: Log token being sent (remove in production)
      console.log('[API] ➤ Request to:', url, '| Token:', token.substring(0, 20) + '...')
    } else {
      console.log('[API] ➤ Request to:', url, '| No token')
    }
    return config
  },
  (error) => {
    console.error('[API] Request error:', error)
    return Promise.reject(error)
  }
)

// Track refresh token attempts to prevent infinite loops
let isRefreshing = false

// Response interceptor to handle errors and token refresh
axiosClient.interceptors.response.use(
  (response) => {
    console.log('[API] ✓ Response from:', response.config.url, '| Status:', response.status)
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
    const url = originalRequest?.url || 'unknown'
    
    console.log('[API] ✗ Error from:', url, '| Status:', error.response?.status, '| Message:', error.message)
    
    // Handle 401 Unauthorized - only for non-auth routes
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry && !isAuthRoute(url)) {
      console.log('[API] 401 detected, attempting token refresh...')
      
      // Prevent multiple simultaneous refresh attempts
      if (isRefreshing) {
        console.log('[API] Already refreshing, rejecting request')
        return Promise.reject(error)
      }
      
      originalRequest._retry = true
      isRefreshing = true
      
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        
        if (!refreshToken) {
          console.log('[API] No refresh token available, triggering logout')
          // No refresh token - force logout
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
          return Promise.reject(error)
        }
        
        console.log('[API] Attempting to refresh token...')
        
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
        
        console.log('[API] Refresh response status:', response.status)
        console.log('[API] Refresh response data:', JSON.stringify(response.data))
        
        const { access_token, refresh_token: newRefreshToken } = response.data
        
        if (!access_token) {
          console.error('[API] No access_token in refresh response!')
          throw new Error('No access token in refresh response')
        }
        
        console.log('[API] New access token received:', access_token.substring(0, 20) + '...')
        
        // Store new tokens
        localStorage.setItem('access_token', access_token)
        if (newRefreshToken) {
          localStorage.setItem('refresh_token', newRefreshToken)
        }
        
        console.log('[API] ✓ Token refreshed successfully')
        
        // Retry the original request with new token
        // The interceptor will pick up the new token from localStorage
        // because we check for existing Authorization header first
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`
        }
        
        isRefreshing = false
        return axiosClient(originalRequest)
      } catch (refreshError) {
        console.error('[API] ✗ Token refresh failed:', refreshError)
        isRefreshing = false
        
        // Clear tokens and trigger logout on refresh failure
        console.log('[API] Clearing tokens and redirecting to login')
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        
        // Only redirect if we're not already on login page
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login'
        }
        
        return Promise.reject(refreshError)
      }
    }
    
    // For auth route 401s, just reject (don't try to refresh)
    if (error.response?.status === 401 && isAuthRoute(url)) {
      console.log('[API] Auth route returned 401')
    }
    
    return Promise.reject(error)
  }
)

export default axiosClient

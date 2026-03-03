/**
 * Centralized API service with proper token handling.
 * This is the SINGLE axios instance for the entire application.
 */
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'

// Use relative URL to work with Vite proxy
const API_BASE_URL = '/api'

// Create the single axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// Request interceptor - ALWAYS attach token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    const url = config.url || ''
    
    // STEP 1: Log token before every request
    console.log('TOKEN USED:', token)
    
    // Skip auth header for login/register/refresh endpoints - exact match to avoid false positives
    const publicEndpoints = ['/auth/login', '/auth/register', '/auth/refresh']
    const isPublicEndpoint = publicEndpoints.some(endpoint => url === endpoint)
    
    if (token && config.headers) {
      // Always set Authorization header for protected endpoints
      if (!isPublicEndpoint) {
        config.headers.Authorization = `Bearer ${token}`
        console.log('[API] ➤ Request to:', url, '| Token attached')
      } else {
        console.log('[API] ➤ Request to:', url, '| Public endpoint - no token')
      }
    } else {
      console.log('[API] ➤ Request to:', url, '| No token')
    }
    
    // STEP 2: Log final headers
    console.log('FINAL HEADERS:', config.headers)
    
    return config
  },
  (error) => {
    console.error('[API] Request interceptor error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor - handle 401 errors
api.interceptors.response.use(
  (response) => {
    console.log('[API] ✓ Response from:', response.config.url, '| Status:', response.status)
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
    const url = originalRequest?.url || 'unknown'
    
    console.log('[API] ✗ Error from:', url, '| Status:', error.response?.status)
    
    // Handle 401 Unauthorized
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      console.log('[API] 401 detected, attempting token refresh...')
      
      const refreshToken = localStorage.getItem('refresh_token')
      
      if (!refreshToken) {
        console.log('[API] No refresh token, redirecting to login')
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(error)
      }
      
      originalRequest._retry = true
      
      try {
        // Use form data for refresh endpoint
        const formData = new URLSearchParams()
        formData.append('refresh_token', refreshToken)
        
        const response = await axios.post(
          `${API_BASE_URL}/auth/refresh`,
          formData,
          {
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
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
        
        console.log('[API] ✓ Token refreshed successfully')
        
        // Retry original request with new token
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`
        }
        
        return api(originalRequest)
      } catch (refreshError) {
        console.error('[API] ✗ Token refresh failed:', refreshError)
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }
    
    return Promise.reject(error)
  }
)

export default api

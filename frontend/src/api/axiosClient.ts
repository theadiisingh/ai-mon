import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'

const MAX_RETRY_COUNT = 1

const axiosClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// Request interceptor to add auth token
axiosClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
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
let refreshTokenAttempts = 0

// Response interceptor to handle errors and token refresh
axiosClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
    
    // Handle 401 Unauthorized
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      // Prevent infinite refresh loops
      if (isRefreshing || refreshTokenAttempts >= MAX_RETRY_COUNT) {
        // Clear tokens and redirect to login
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
      
      originalRequest._retry = true
      isRefreshing = true
      refreshTokenAttempts++
      
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        
        if (refreshToken) {
          // Attempt to refresh the token
          const response = await axios.post(
            `${import.meta.env.VITE_API_URL || '/api'}/auth/refresh`,
            {},
            {
              headers: {
                Authorization: `Bearer ${refreshToken}`,
              },
            }
          )
          
          const { access_token, refresh_token: newRefreshToken } = response.data
          
          // Store new tokens
          localStorage.setItem('access_token', access_token)
          if (newRefreshToken) {
            localStorage.setItem('refresh_token', newRefreshToken)
          }
          
          // Reset refresh counter on success
          refreshTokenAttempts = 0
          
          // Retry the original request
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`
          }
          isRefreshing = false
          return axiosClient(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed - clear tokens and redirect to login
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        refreshTokenAttempts = 0
        
        // Redirect to login if in browser context
        if (typeof window !== 'undefined') {
          window.location.href = '/login'
        }
      } finally {
        isRefreshing = false
      }
    }
    
    return Promise.reject(error)
  }
)

export default axiosClient

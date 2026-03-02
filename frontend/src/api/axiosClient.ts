import axios from 'axios'

const axiosClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
axiosClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors
axiosClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Don't redirect automatically - let the AuthContext handle logout
    // This prevents the site from going down on page reload
    if (error.response?.status === 401) {
      // Just reject, don't redirect immediately
      // The AuthContext will handle the logout on next auth check
    }
    return Promise.reject(error)
  }
)

export default axiosClient

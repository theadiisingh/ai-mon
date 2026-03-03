import api from './api'
import { User, UserCreate, Token } from '../types/user'

// Register response includes user + tokens
interface RegisterResponse {
  user: User
  access_token: string
  refresh_token: string
  token_type: string
}

export const authApi = {
  register: (data: UserCreate) => api.post<RegisterResponse>('/auth/register', data),
  
  login: (email: string, password: string) => {
    // Backend uses OAuth2PasswordRequestForm which requires form data, not JSON
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)
    return api.post<Token>('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
  },
  
  me: () => api.get<User>('/users/me'),
  
  refreshToken: () => {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      return Promise.reject(new Error('No refresh token available'))
    }
    // Use form data for OAuth2 refresh token endpoint
    const formData = new URLSearchParams()
    formData.append('grant_type', 'refresh_token')
    return api.post<Token>('/auth/refresh', formData, {
      headers: { 
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': `Bearer ${refreshToken}`
      }
    })
  },
}

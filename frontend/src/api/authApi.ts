import axiosClient from './axiosClient'
import { User, UserCreate, Token } from '../types/user'

export const authApi = {
  register: (data: UserCreate) => axiosClient.post<Token>('/auth/register', data),
  
  login: (email: string, password: string) => {
    // Backend uses OAuth2PasswordRequestForm which requires form data, not JSON
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)
    return axiosClient.post<Token>('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
  },
  
  me: () => axiosClient.get<User>('/users/me'),
  
  refreshToken: () => axiosClient.post<Token>('/auth/refresh'),
}

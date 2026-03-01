import axiosClient from './axiosClient'
import { User, UserCreate, Token } from '../types/user'

export const authApi = {
  register: (data: UserCreate) => axiosClient.post<Token>('/auth/register', data),
  
  login: (email: string, password: string) => 
    axiosClient.post<Token>('/auth/login', { email, password }),
  
  me: () => axiosClient.get<User>('/auth/me'),
  
  refreshToken: () => axiosClient.post<Token>('/auth/refresh'),
}

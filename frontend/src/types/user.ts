export interface User {
  id: number
  email: string
  username: string
  full_name?: string
  created_at: string
  updated_at: string
  is_active: boolean
  is_superuser: boolean
}

export interface UserCreate {
  email: string
  username: string
  password: string
  full_name?: string
}

export interface UserUpdate {
  email?: string
  username?: string
  password?: string
  full_name?: string
}

export interface Token {
  access_token: string
  refresh_token: string
  token_type?: string
}

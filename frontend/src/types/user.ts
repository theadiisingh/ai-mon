export interface User {
  id: number
  email: string
  username: string
  created_at: string
}

export interface UserCreate {
  email: string
  username: string
  password: string
}

export interface UserUpdate {
  email?: string
  username?: string
  password?: string
}

export interface Token {
  access_token: string
  token_type: string
}

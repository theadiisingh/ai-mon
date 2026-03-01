export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | 'HEAD' | 'OPTIONS'

export interface ApiEndpoint {
  id: number
  user_id: number
  name: string
  url: string
  method: HttpMethod
  headers: string | null
  body: string | null
  expected_status_code: number
  timeout_seconds: number
  interval_seconds: number
  is_active: boolean
  is_paused: boolean
  created_at: string
  updated_at: string
  // Last check results
  last_status_code: number | null
  last_response_time: number | null
  last_checked_at: string | null
  // Stats
  total_checks: number
  successful_checks: number
  failed_checks: number
  uptime_percentage: number
  avg_response_time: number | null
}

export interface ApiEndpointCreate {
  name: string
  url: string
  method: HttpMethod
  headers?: string
  body?: string
  expected_status_code: number
  timeout_seconds: number
  interval_seconds: number
}

export interface ApiEndpointUpdate {
  name?: string
  url?: string
  method?: HttpMethod
  headers?: string
  body?: string
  expected_status_code?: number
  timeout_seconds?: number
  interval_seconds?: number
  is_active?: boolean
}

export interface ApiEndpointListResponse {
  items: ApiEndpoint[]
  total: number
  page: number
  page_size: number
}

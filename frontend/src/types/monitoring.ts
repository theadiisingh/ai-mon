export type CheckStatus = 'success' | 'failure' | 'error' | 'timeout'

export interface MonitoringLog {
  id: number
  api_endpoint_id: number
  user_id: number
  status: CheckStatus
  status_code: number | null
  response_time: number | null
  error_message: string | null
  is_anomaly: boolean
  anomaly_score: number | null
  request_method: string
  request_url: string
  response_body: string | null
  checked_at: string
}

export interface MonitoringLogListResponse {
  items: MonitoringLog[]
  total: number
  page: number
  page_size: number
}

export interface Anomaly {
  log_id: number
  checked_at: string
  response_time: number
  status_code: number
  anomaly_score: number
}

export interface Metrics {
  total_checks: number
  successful_checks: number
  failed_checks: number
  error_rate: number
  uptime_percentage: number
  avg_response_time: number
  min_response_time: number
  max_response_time: number
}

export interface Uptime {
  total_checks: number
  successful_checks: number
  uptime_percentage: number
}

export interface TimeSeriesPoint {
  timestamp: string
  value: number
}

export interface StatusCodeDistribution {
  [key: string]: number
}

export interface AIInsight {
  id: number
  api_endpoint_id: number
  user_id: number
  insight_type: string
  severity: string
  title: string
  summary: string
  possible_causes: string | null
  suggested_steps: string | null
  related_logs_summary: string | null
  triggered_by_log_id: number | null
  confidence_score: number | null
  model_used: string | null
  tokens_used: number | null
  created_at: string
}

// Backend expects: api_endpoint_id, time_range_hours, log_ids, analysis_type
export interface AIAnalysisRequest {
  api_endpoint_id: number
  time_range_hours?: number
  log_ids?: number[]
  analysis_type?: string
}

export interface AIAnalysisResponse {
  summary: string
  possible_causes: string[]
  suggested_steps: string[]
  confidence_score: number
  model_used: string
  tokens_used: number
}

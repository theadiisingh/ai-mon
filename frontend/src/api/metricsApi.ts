import api from './api'
import { 
  MonitoringLog, 
  MonitoringLogListResponse, 
  Metrics, 
  Uptime, 
  TimeSeriesPoint, 
  AIInsight,
  AIAnalysisResponse 
} from '../types/monitoring'

export const metricsApi = {
  // Monitoring Logs - Backend: /api/monitoring/logs
  getLogs: (params?: { 
    api_endpoint_id?: number; 
    page?: number; 
    page_size?: number; 
    status_filter?: string;
  }) => api.get<MonitoringLogListResponse>('/monitoring/logs', { params }),
  
  getLog: (id: number) => api.get<MonitoringLog>(`/monitoring/logs/${id}`),
  
  // Metrics - Backend: /api/metrics/*
  // Pass endpointId as undefined to get aggregated metrics for all endpoints
  getMetrics: (endpointId: number | undefined, hours?: number) => 
    api.get<Metrics>('/metrics/overview', { params: { 
      ...(endpointId && { api_endpoint_id: endpointId }),
      hours: hours || 24 
    }}),
  
  getUptime: (endpointId: number | undefined, days?: number) => 
    api.get<Uptime>('/metrics/uptime', { params: { 
      ...(endpointId && { api_endpoint_id: endpointId }),
      days: days || 7
    }}),
  
  getResponseTimeSeries: (endpointId: number, hours?: number) => 
    api.get<TimeSeriesPoint[]>('/metrics/response-time', { 
      params: { api_endpoint_id: endpointId, hours } 
    }),
  
  getStatusCodeDistribution: (endpointId: number, hours?: number) => 
    api.get<Record<string, number>>('/metrics/status-codes', { 
      params: { api_endpoint_id: endpointId, hours } 
    }),
  
  getErrorRate: (endpointId: number, hours?: number) => 
    api.get<{error_rate: number}>('/metrics/error-rate', { 
      params: { api_endpoint_id: endpointId, hours } 
    }),
  
  getAnomalies: (endpointId: number, hours?: number) => 
    api.get<MonitoringLog[]>(`/monitoring/endpoints/${endpointId}/anomalies`, { 
      params: { window_hours: hours } 
    }),
  
  getBaseline: (endpointId: number, hours?: number) => 
    api.get<{avg: number, std: number, min: number, max: number, p95: number, p99: number}>(
      `/monitoring/endpoints/${endpointId}/baseline`, { 
      params: { window_hours: hours } 
    }),
  
  // AI Analysis - Backend: /api/monitoring/analyze
  triggerAnalysis: (endpointId: number, hours?: number, logIds?: number[]) => 
    api.post<AIAnalysisResponse>('/monitoring/analyze', { 
      api_endpoint_id: endpointId,
      time_range_hours: hours || 24,
      log_ids: logIds
    }),
  
  // Health Check Status - Backend: /api/metrics/health-check/status
  getHealthStatus: () => 
    api.get<{is_running: boolean, active_tasks: number, paused_tasks: number}>('/metrics/health-check/status'),
  
  // AI Insights - Backend: /api/monitoring/endpoints/{id}/insights
  getInsights: (endpointId: number) => 
    api.get<AIInsight[]>(`/monitoring/endpoints/${endpointId}/insights`),
}

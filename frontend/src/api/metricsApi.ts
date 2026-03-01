import axiosClient from './axiosClient'
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
  }) => axiosClient.get<MonitoringLogListResponse>('/monitoring/logs', { params }),
  
  getLog: (id: number) => axiosClient.get<MonitoringLog>(`/monitoring/logs/${id}`),
  
  // Metrics - Backend: /api/metrics/*
  getMetrics: (endpointId: number, hours?: number) => 
    axiosClient.get<Metrics>('/metrics/overview', { params: { api_endpoint_id: endpointId, hours } }),
  
  getUptime: (endpointId: number, days?: number) => 
    axiosClient.get<Uptime>('/metrics/uptime', { params: { api_endpoint_id: endpointId, days } }),
  
  getResponseTimeSeries: (endpointId: number, hours?: number) => 
    axiosClient.get<TimeSeriesPoint[]>('/metrics/response-time', { 
      params: { api_endpoint_id: endpointId, hours } 
    }),
  
  getStatusCodeDistribution: (endpointId: number, hours?: number) => 
    axiosClient.get<Record<string, number>>('/metrics/status-codes', { 
      params: { api_endpoint_id: endpointId, hours } 
    }),
  
  getErrorRate: (endpointId: number, hours?: number) => 
    axiosClient.get<{error_rate: number}>('/metrics/error-rate', { 
      params: { api_endpoint_id: endpointId, hours } 
    }),
  
  getAnomalies: (endpointId: number, hours?: number) => 
    axiosClient.get<MonitoringLog[]>(`/monitoring/endpoints/${endpointId}/anomalies`, { 
      params: { window_hours: hours } 
    }),
  
  getBaseline: (endpointId: number, hours?: number) => 
    axiosClient.get<{avg: number, std: number, min: number, max: number, p95: number, p99: number}>(
      `/monitoring/endpoints/${endpointId}/baseline`, { 
      params: { window_hours: hours } 
    }),
  
  // AI Analysis - Backend: /api/monitoring/analyze
  triggerAnalysis: (endpointId: number, hours?: number, logIds?: number[]) => 
    axiosClient.post<AIAnalysisResponse>('/monitoring/analyze', { 
      api_endpoint_id: endpointId,
      time_range_hours: hours || 24,
      log_ids: logIds
    }),
  
  // Health Check Status - Backend: /api/metrics/health-check/status
  getHealthStatus: () => 
    axiosClient.get<{is_running: boolean, active_tasks: number, paused_tasks: number}>('/metrics/health-check/status'),
}

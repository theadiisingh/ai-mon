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
  // Monitoring Logs
  getLogs: (params?: { 
    endpoint_id?: number; 
    page?: number; 
    page_size?: number; 
    status?: string;
    start_date?: string;
    end_date?: string;
  }) => axiosClient.get<MonitoringLogListResponse>('/monitoring/logs', { params }),
  
  getLog: (id: number) => axiosClient.get<MonitoringLog>(`/monitoring/logs/${id}`),
  
  // Metrics
  getMetrics: (endpointId: number, hours?: number) => 
    axiosClient.get<Metrics>(`/monitoring/metrics/${endpointId}`, { params: { hours } }),
  
  getUptime: (endpointId: number, days?: number) => 
    axiosClient.get<Uptime>(`/monitoring/uptime/${endpointId}`, { params: { days } }),
  
  getResponseTimeSeries: (endpointId: number, hours?: number) => 
    axiosClient.get<TimeSeriesPoint[]>(`/monitoring/timeseries/response-time/${endpointId}`, { 
      params: { hours } 
    }),
  
  getStatusCodeDistribution: (endpointId: number, hours?: number) => 
    axiosClient.get<Record<string, number>>(`/monitoring/distribution/status-codes/${endpointId}`, { 
      params: { hours } 
    }),
  
  getAnomalies: (endpointId: number, hours?: number) => 
    axiosClient.get<MonitoringLog[]>(`/monitoring/anomalies/${endpointId}`, { 
      params: { hours } 
    }),
  
  // AI Insights
  getInsights: (endpointId: number) => 
    axiosClient.get<AIInsight[]>(`/monitoring/insights/${endpointId}`),
  
  triggerAnalysis: (endpointId: number, hours?: number) => 
    axiosClient.post<AIAnalysisResponse>(`/monitoring/analyze/${endpointId}`, { hours }),
}

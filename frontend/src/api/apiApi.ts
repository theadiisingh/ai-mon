import api from './api'
import { ApiEndpoint, ApiEndpointCreate, ApiEndpointUpdate, ApiEndpointListResponse } from '../types/api'

export const apiApi = {
  list: (params?: { page?: number; page_size?: number; search?: string }) =>
    api.get<ApiEndpointListResponse>('/apis/', { params }),
  
  get: (id: number) => api.get<ApiEndpoint>(`/apis/${id}`),
  
  create: (data: ApiEndpointCreate) =>
    api.post<ApiEndpoint>('/apis/', data),
  
  update: (id: number, data: ApiEndpointUpdate) =>
    api.put<ApiEndpoint>(`/apis/${id}`, data),
  
  delete: (id: number) => api.delete(`/apis/${id}`),
  
  toggle: (id: number) => api.post<ApiEndpoint>(`/apis/${id}/toggle`),
}

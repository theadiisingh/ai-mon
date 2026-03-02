import axiosClient from './axiosClient'
import { ApiEndpoint, ApiEndpointCreate, ApiEndpointUpdate, ApiEndpointListResponse } from '../types/api'

export const apiApi = {
  list: (params?: { page?: number; page_size?: number; search?: string }) =>
    axiosClient.get<ApiEndpointListResponse>('/apis', { params }),
  
  get: (id: number) => axiosClient.get<ApiEndpoint>(`/apis/${id}`),
  
  create: (data: ApiEndpointCreate) =>
    axiosClient.post<ApiEndpoint>('/apis', data),
  
  update: (id: number, data: ApiEndpointUpdate) =>
    axiosClient.put<ApiEndpoint>(`/apis/${id}`, data),
  
  delete: (id: number) => axiosClient.delete(`/apis/${id}`),
  
  toggle: (id: number) => axiosClient.post<ApiEndpoint>(`/apis/${id}/toggle`),
}

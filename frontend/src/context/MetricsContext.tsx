/**
 * Metrics Context - Centralized state management for monitoring metrics
 * 
 * This context provides a single source of truth for all metrics data.
 * All pages read from this shared state instead of fetching independently.
 * 
 * Backend is the single source of truth - frontend only renders.
 */
import { createContext, useContext, ReactNode, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { metricsApi } from '../api/metricsApi'
import { Metrics, Uptime } from '../types/monitoring'

interface MetricsContextType {
  // Aggregated metrics for all endpoints
  metrics: Metrics | undefined
  metricsLoading: boolean
  metricsError: Error | null
  
  // Uptime data
  uptime: Uptime | undefined
  uptimeLoading: boolean
  uptimeError: Error | null
  
  // Refresh function
  refetch: () => void
  isRefetching: boolean
}

const MetricsContext = createContext<MetricsContextType | undefined>(undefined)

interface MetricsProviderProps {
  children: ReactNode
}

export function MetricsProvider({ children }: MetricsProviderProps) {
  // Fetch aggregated metrics for all endpoints - single source of truth
  const { 
    data: metrics, 
    isLoading: metricsLoading, 
    error: metricsError,
    refetch: refetchMetrics,
    isRefetching: metricsRefetching
  } = useQuery({
    queryKey: ['metrics', 'overview', 'all'],
    queryFn: async () => {
      const response = await metricsApi.getMetrics(undefined, 24)
      return response.data
    },
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // Refresh every minute
  })

  // Fetch uptime data for all endpoints
  const { 
    data: uptime, 
    isLoading: uptimeLoading, 
    error: uptimeError,
    refetch: refetchUptime,
    isRefetching: uptimeRefetching
  } = useQuery({
    queryKey: ['metrics', 'uptime', 'all'],
    queryFn: async () => {
      const response = await metricsApi.getUptime(undefined, 7)
      return response.data
    },
    staleTime: 60000, // 1 minute
    refetchInterval: 120000, // Refresh every 2 minutes
  })

  const value = useMemo<MetricsContextType>(() => ({
    metrics,
    metricsLoading,
    metricsError: metricsError as Error | null,
    
    uptime,
    uptimeLoading,
    uptimeError: uptimeError as Error | null,
    
    refetch: () => {
      refetchMetrics()
      refetchUptime()
    },
    isRefetching: metricsRefetching || uptimeRefetching
  }), [
    metrics,
    metricsLoading,
    metricsError,
    uptime,
    uptimeLoading,
    uptimeError,
    refetchMetrics,
    refetchUptime,
    metricsRefetching,
    uptimeRefetching
  ])

  return (
    <MetricsContext.Provider value={value}>
      {children}
    </MetricsContext.Provider>
  )
}

/**
 * Hook to access centralized metrics data.
 * Use this instead of direct API calls for global metrics.
 */
export function useMetrics() {
  const context = useContext(MetricsContext)
  if (context === undefined) {
    throw new Error('useMetrics must be used within a MetricsProvider')
  }
  return context
}

/**
 * Hook to get metrics for a specific endpoint.
 * This still uses backend as single source of truth.
 */
export function useEndpointMetrics(endpointId: number | undefined) {
  const { 
    data: metrics, 
    isLoading, 
    error,
    refetch,
    isRefetching
  } = useQuery({
    queryKey: ['metrics', 'endpoint', endpointId],
    queryFn: async () => {
      if (!endpointId) return null
      const response = await metricsApi.getMetrics(endpointId, 24)
      return response.data
    },
    enabled: !!endpointId,
    staleTime: 30000,
    refetchInterval: 60000,
  })

  return {
    metrics: metrics as Metrics | null,
    loading: isLoading,
    error: error as Error | null,
    refetch,
    isRefetching
  }
}

/**
 * Hook to get uptime for a specific endpoint.
 */
export function useEndpointUptime(endpointId: number | undefined, days: number = 7) {
  const { 
    data: uptime, 
    isLoading, 
    error,
    refetch,
    isRefetching
  } = useQuery({
    queryKey: ['metrics', 'uptime', endpointId, days],
    queryFn: async () => {
      if (!endpointId) return null
      const response = await metricsApi.getUptime(endpointId, days)
      return response.data
    },
    enabled: !!endpointId,
    staleTime: 60000,
    refetchInterval: 120000,
  })

  return {
    uptime: uptime as Uptime | null,
    loading: isLoading,
    error: error as Error | null,
    refetch,
    isRefetching
  }
}


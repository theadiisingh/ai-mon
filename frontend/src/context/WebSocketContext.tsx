/**
 * WebSocket Context - Global WebSocket connection for real-time updates
 * 
 * This context provides a single WebSocket connection that:
 * 1. Listens for monitoring updates from the backend
 * 2. Triggers React Query cache invalidation to refresh data
 * 3. Updates local state for instant UI feedback
 */
import { createContext, useContext, useCallback, ReactNode } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useWebSocketMonitor, MonitoringUpdate } from '../hooks/useWebSocketMonitor'
import { useAuth } from '../hooks/useAuth'

interface WebSocketContextType {
  isConnected: boolean
  lastUpdate: MonitoringUpdate | null
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined)

interface WebSocketProviderProps {
  children: ReactNode
}

export function WebSocketProvider({ children }: WebSocketProviderProps) {
  const queryClient = useQueryClient()
  const { isAuthenticated } = useAuth()
  
  // Handle incoming WebSocket messages
  const handleUpdate = useCallback((update: MonitoringUpdate) => {
    console.log('[WebSocket] Received update:', update)
    
    // Invalidate queries to trigger a refetch from the backend
    // This ensures all data comes from the backend API, not local calculations
    
    if (update.type === 'endpoint_update' || update.type === 'health_check_complete') {
      const endpointId = update.endpoint_id
      
      // Invalidate specific endpoint queries
      queryClient.invalidateQueries({ queryKey: ['api', endpointId] })
      queryClient.invalidateQueries({ queryKey: ['apis'] })
      
      // Invalidate metrics queries (both global and per-endpoint)
      queryClient.invalidateQueries({ queryKey: ['metrics', 'overview'] })
      queryClient.invalidateQueries({ queryKey: ['metrics', 'endpoint', endpointId] })
      queryClient.invalidateQueries({ queryKey: ['metrics', 'uptime', endpointId] })
      
      // Invalidate logs for this endpoint
      queryClient.invalidateQueries({ queryKey: ['logs', endpointId] })
      
      // Invalidate latency/history data
      queryClient.invalidateQueries({ queryKey: ['latency', endpointId] })
      
      console.log('[WebSocket] Triggered data refresh for endpoint:', endpointId)
    }
  }, [queryClient])
  
  // Connect to WebSocket when authenticated
  const { isConnected, lastMessage } = useWebSocketMonitor({
    onUpdate: handleUpdate,
    enabled: isAuthenticated,
  })
  
  const value: WebSocketContextType = {
    isConnected,
    lastUpdate: lastMessage || null,
  }
  
  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  )
}

/**
 * Hook to access WebSocket connection status
 */
export function useWebSocket() {
  const context = useContext(WebSocketContext)
  if (context === undefined) {
    // Return default values if not in provider (e.g., on login page)
    return {
      isConnected: false,
      lastUpdate: null,
    }
  }
  return context
}


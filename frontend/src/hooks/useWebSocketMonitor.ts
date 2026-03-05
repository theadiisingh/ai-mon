/**
 * WebSocket hook for real-time monitoring updates.
 * 
 * This hook connects to the backend WebSocket endpoint and listens
 * for health check updates. When an update is received, it triggers
 * a callback to refresh the data from the backend.
 */
import { useEffect, useRef, useCallback } from 'react'
import useWebSocket, { ReadyState } from 'react-use-websocket'

// Get WebSocket URL based on current location
function getWebSocketUrl(): string {
  if (typeof window === 'undefined') {
    return 'ws://localhost:8000/ws/monitor-updates'
  }
  
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.host
  return `${protocol}//${host}/ws/monitor-updates`
}

export interface MonitoringUpdate {
  type: 'endpoint_update' | 'health_check_complete'
  endpoint_id: number
  status: string
  latency: number
  timestamp: string
  uptime_percentage?: number
  total_checks?: number
  failed_checks?: number
  status_code?: number
  endpoint_name?: string
  is_success?: boolean
}

interface UseWebSocketMonitorOptions {
  onUpdate?: (update: MonitoringUpdate) => void
  enabled?: boolean
}

export function useWebSocketMonitor({ 
  onUpdate, 
  enabled = true 
}: UseWebSocketMonitorOptions = {}) {
  const hasListenersRef = useRef(false)
  
  const {
    sendJsonMessage,
    lastJsonMessage,
    readyState,
  } = useWebSocket<MonitoringUpdate>(getWebSocketUrl(), {
    // Only connect when enabled and user is authenticated
    shouldReconnect: () => enabled,
    
    // Reconnect on disconnect
    reconnectAttempts: 10,
    reconnectInterval: 3000,
    
    // Don't filter messages - handle all at application level
    filter: () => false,
    
    // Share the connection across the app
    share: true,
  })
  
  // Handle incoming messages
  useEffect(() => {
    if (lastJsonMessage && onUpdate && !hasListenersRef.current) {
      hasListenersRef.current = true
      
      // Call the onUpdate callback with the received message
      onUpdate(lastJsonMessage)
      
      // Reset for next message
      hasListenersRef.current = false
    }
  }, [lastJsonMessage, onUpdate])
  
  // Helper to check if connected
  const isConnected = readyState === ReadyState.OPEN
  
  // Helper to send a ping
  const sendPing = useCallback(() => {
    if (isConnected) {
      sendJsonMessage({ type: 'ping' })
    }
  }, [isConnected, sendJsonMessage])
  
  return {
    isConnected,
    sendPing,
    lastMessage: lastJsonMessage,
  }
}

/**
 * Hook to get the connection status display string
 */
export function useWebSocketStatus(): string {
  const { isConnected } = useWebSocketMonitor({ enabled: false })
  
  if (isConnected) return 'Connected'
  return 'Disconnected'
}


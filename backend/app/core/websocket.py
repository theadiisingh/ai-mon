"""
WebSocket manager for real-time monitoring updates.
Broadcasts health check results to all connected clients.
"""
import json
import asyncio
from typing import Dict, Set, Any, Optional
from datetime import datetime
from loguru import logger


class WebSocketManager:
    """
    Manages WebSocket connections and broadcasts monitoring updates.
    Implements singleton pattern for global access.
    """
    
    _instance: Optional['WebSocketManager'] = None
    _lock: asyncio.Lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._connections: Set[Any] = set()
        logger.info("WebSocketManager initialized")
    
    async def connect(self, websocket: Any) -> None:
        """Register a new WebSocket connection."""
        self._connections.add(websocket)
        logger.info(f"WebSocket client connected. Total connections: {len(self._connections)}")
    
    async def disconnect(self, websocket: Any) -> None:
        """Remove a WebSocket connection."""
        self._connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total connections: {len(self._connections)}")
    
    async def broadcast(self, message: Dict[str, Any]) -> None:
        """
        Broadcast a message to all connected clients.
        
        Args:
            message: Dictionary containing the update data
                     Expected fields:
                     - endpoint_id: int
                     - status: str ("UP" or "DOWN")
                     - latency: float (response time in ms)
                     - timestamp: str (ISO format)
                     - uptime_percentage: float
                     - total_checks: int
                     - failed_checks: int
        """
        if not self._connections:
            return
        
        # Add timestamp to message
        message["broadcast_at"] = datetime.utcnow().isoformat()
        
        # Serialize message
        message_json = json.dumps(message)
        
        # Create list of connections to avoid modification during iteration
        connections_snapshot = list(self._connections)
        
        # Track failed connections for cleanup
        disconnected = []
        
        # Send to all connected clients
        for connection in connections_snapshot:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send WebSocket message: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            await self.disconnect(connection)
        
        if disconnected:
            logger.info(f"Cleaned up {len(disconnected)} dead WebSocket connections")
    
    async def broadcast_endpoint_update(
        self,
        endpoint_id: int,
        status: str,
        latency: float,
        uptime_percentage: float,
        total_checks: int,
        failed_checks: int,
        status_code: Optional[int] = None
    ) -> None:
        """
        Broadcast an endpoint status update.
        
        Args:
            endpoint_id: ID of the monitored endpoint
            status: "UP" or "DOWN"
            latency: Response time in milliseconds
            uptime_percentage: Uptime percentage (0-100)
            total_checks: Total number of checks performed
            failed_checks: Number of failed checks
            status_code: HTTP status code from the check (optional)
        """
        message = {
            "type": "endpoint_update",
            "endpoint_id": endpoint_id,
            "status": status,
            "latency": latency,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_percentage": uptime_percentage,
            "total_checks": total_checks,
            "failed_checks": failed_checks,
        }
        
        if status_code is not None:
            message["status_code"] = status_code
        
        await self.broadcast(message)
    
    async def broadcast_health_check_complete(
        self,
        endpoint_id: int,
        endpoint_name: str,
        status: str,
        latency: float,
        is_success: bool
    ) -> None:
        """
        Broadcast a completed health check result.
        
        Args:
            endpoint_id: ID of the monitored endpoint
            endpoint_name: Name of the endpoint
            status: Check status ("SUCCESS", "FAILURE", "TIMEOUT", "ERROR")
            latency: Response time in milliseconds
            is_success: Whether the check was successful
        """
        message = {
            "type": "health_check_complete",
            "endpoint_id": endpoint_id,
            "endpoint_name": endpoint_name,
            "status": status,
            "latency": latency,
            "is_success": is_success,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        await self.broadcast(message)
    
    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self._connections)
    
    async def clear_connections(self) -> None:
        """Clear all connections (used for testing or shutdown)."""
        self._connections.clear()
        logger.info("All WebSocket connections cleared")


# Global instance getter
def get_websocket_manager() -> WebSocketManager:
    """Get the global WebSocket manager instance."""
    return WebSocketManager()


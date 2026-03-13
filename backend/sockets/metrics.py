"""
WebSocket Metrics Streaming Service.

This module provides real-time metrics streaming to the dashboard
via WebSocket connections.

Example flow:
    Interview runtime
    ↓
    metrics stream
    ↓
    WebSocket
    ↓
    dashboard updates live
"""

import asyncio
from typing import Any, Dict, Set

from fastapi import WebSocket, WebSocketDisconnect

from backend.utils.metrics import metrics
from backend.utils.logger import get_logger
# Import JWT service for token validation
from backend.auth.jwt_service import verify_token, TokenData

logger = get_logger(__name__)


class MetricsSocket:
    """
    Manages WebSocket connections for real-time metrics streaming.
    
    Usage:
        metrics_socket = MetricsSocket()
        
        @app.websocket("/ws/metrics")
        async def metrics_ws(websocket: WebSocket):
            await metrics_socket.handle(ws)
    """
    
    def __init__(self, broadcast_interval: float = 2.0):
        """
        Initialize the metrics socket handler.
        
        Args:
            broadcast_interval: Interval in seconds between metric broadcasts
        """
        self.broadcast_interval = broadcast_interval
        self._connections: Set[WebSocket] = set()
        self._running = False
    
    async def handle(self, websocket: WebSocket):
        """
        Handle a WebSocket connection for metrics streaming.
        
        Args:
            websocket: The WebSocket connection
        """
        # Validate JWT token during handshake
        token = websocket.query_params.get("token")
        if not token:
            await websocket.accept()
            await websocket.send_json({
                "type": "error",
                "code": "UNAUTHORIZED",
                "message": "Missing authentication token",
                "recoverable": True,
            })
            await websocket.close(code=1008)
            return
        
        try:
            user_data: TokenData = verify_token(token)
            # Store user data in connection state for later use
            websocket.state.user = user_data
        except Exception:
            await websocket.accept()
            await websocket.send_json({
                "type": "error",
                "code": "UNAUTHORIZED",
                "message": "Invalid authentication token",
                "recoverable": True,
            })
            await websocket.close(code=1008)
            return
        
        await websocket.accept()
        self._connections.add(websocket)
        
        try:
            while True:
                # Get current metrics snapshot
                metrics_data = self._get_metrics_snapshot()
                
                # Send metrics to client
                await websocket.send_json(metrics_data)
                
                # Wait before next update
                await asyncio.sleep(self.broadcast_interval)
                
        except WebSocketDisconnect:
            logger.info("Metrics WebSocket disconnected")
        except asyncio.CancelledError:
            logger.info("Metrics WebSocket task cancelled")
            raise
        except Exception:
            logger.exception("Metrics WebSocket handler failed")
        finally:
            self._connections.discard(websocket)
    
    async def broadcast(self, data: Dict[str, Any]):
        """
        Broadcast data to all connected clients.
        
        Args:
            data: Data to broadcast
        """
        disconnected = set()
        
        for ws in self._connections:
            try:
                await ws.send_json(data)
            except Exception:
                logger.warning("Dropping disconnected metrics websocket client")
                disconnected.add(ws)
        
        # Clean up disconnected clients
        for ws in disconnected:
            self._connections.discard(ws)
    
    def _get_metrics_snapshot(self) -> Dict[str, Any]:
        """
        Get a snapshot of current metrics.
        
        Returns:
            Dictionary containing current metrics
        """
        snapshot = metrics.snapshot()
        
        # Add timestamp
        from datetime import datetime
        snapshot["timestamp"] = datetime.utcnow().isoformat()
        
        # Add derived metrics
        snapshot["derived"] = self._calculate_derived_metrics(snapshot)
        
        return snapshot
    
    def _calculate_derived_metrics(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate derived metrics from raw metrics.
        
        Args:
            snapshot: Raw metrics snapshot
            
        Returns:
            Dictionary containing derived metrics
        """
        derived = {}
        
        # Calculate requests per second
        latencies = snapshot.get("latency_percentiles", {}).get("request_total", {})
        if latencies:
            # Simple estimation based on request count
            request_count = snapshot.get("request", 0)
            derived["requests_per_minute"] = request_count  # This would need time window
        
        # Calculate throughput (tokens per second)
        avg_latencies = snapshot.get("avg_latency", {})
        if avg_latencies:
            # Estimate tokens per second based on latency
            avg_latency = avg_latencies.get("evaluation", 0)
            if avg_latency > 0:
                # Assume average 500 tokens per request
                derived["estimated_tokens_per_second"] = round(500 / avg_latency, 2)
        
        return derived


# Singleton instance
metrics_socket = MetricsSocket(broadcast_interval=2.0)


# =========================================================
# Additional Metrics Functions
# =========================================================

def get_latest_metrics() -> Dict[str, Any]:
    """
    Get the latest metrics for WebSocket streaming.
    
    Returns:
        Dictionary containing latest metrics
    """
    return metrics_socket._get_metrics_snapshot()


async def start_metrics_broadcast():
    """Start broadcasting metrics to connected clients."""
    metrics_socket._running = True
    
    try:
        while metrics_socket._running:
            snapshot = metrics_socket._get_metrics_snapshot()
            await metrics_socket.broadcast(snapshot)
            await asyncio.sleep(metrics_socket.broadcast_interval)
    except asyncio.CancelledError:
        logger.info("Metrics broadcast task cancelled")
        raise
    except Exception:
        logger.exception("Metrics broadcast loop failed")
    finally:
        metrics_socket._running = False


async def stop_metrics_broadcast():
    """Stop broadcasting metrics."""
    metrics_socket._running = False


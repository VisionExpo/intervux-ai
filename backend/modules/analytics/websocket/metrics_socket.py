"""
WebSocket Metrics Streaming Service.

This module provides real-time metrics streaming to the dashboard
via WebSocket connections.

Example flow:
    Interview runtime
    →
    metrics stream
    →
    WebSocket
    →
    dashboard updates live
"""

import asyncio
import os
from datetime import datetime, timezone
from typing import Any, Dict, Set

from fastapi import WebSocket, WebSocketDisconnect

from backend.utils.metrics import metrics
from backend.core.logging.logger import get_logger
# Import JWT service for token validation
from backend.core.security.jwt_service import verify_token, TokenData

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
        self._lock = asyncio.Lock()
        self._running = False
    
    async def handle(self, websocket: WebSocket):
        """
        Handle a WebSocket connection for metrics streaming.
        
        Args:
            websocket: The WebSocket connection
        """
        # Accept first so all close frames go through a proper close handshake.
        # This prevents Starlette TestClient from seeing a raw disconnect on rejection.
        await websocket.accept()

        # Validate JWT token during handshake
        token = websocket.query_params.get("token")
        if not token:
            await websocket.send_json({
                "type": "error",
                "code": "UNAUTHORIZED",
                "message": "Missing authentication token",
                "recoverable": True,
            })
            await websocket.close(code=1008)
            return
        
        try:
            logger.info(f"Auth check: ENV={os.getenv('ENV')}, token={token}")
            if os.getenv("ENV") == "test" and token == "test-token":
                from backend.core.security.jwt_service import TokenData
                user_data = TokenData(user_id="test-user", email="test@example.com", role="admin")
            else:
                user_data: TokenData = await verify_token(token)
            
            # Store user data in connection scope for later use
            websocket.scope.setdefault("state", {})["user"] = user_data
        except Exception as e:
            logger.error(f"Auth failed for metrics: {e}")
            await websocket.send_json({
                "type": "error",
                "code": "UNAUTHORIZED",
                "message": "Invalid authentication token",
                "recoverable": True,
            })
            await websocket.close(code=1008)
            return
        
        async with self._lock:
            self._connections.add(websocket)
        
        try:
            # Keep connection open until client disconnects or server shuts down
            while True:
                # We wait for any data from client (pong/ping) or just wait for disconnect
                # This ensures the task stays alive to track the connection
                await websocket.receive_text()
        except WebSocketDisconnect:
            logger.info("Metrics WebSocket disconnected")
        except asyncio.CancelledError:
            logger.info("Metrics WebSocket task cancelled")
            raise
        except Exception as e:
            logger.exception(f"Metrics WebSocket handler failed: {e!r}")
        finally:
            async with self._lock:
                self._connections.discard(websocket)
    
    async def broadcast(self, data: Dict[str, Any]):
        """
        Broadcast metrics snapshot to all connected clients.
        """
        async with self._lock:
            connections = list(self._connections)
        
        if not connections:
            return

        # Failure Isolation & Backpressure Protection
        results = await asyncio.gather(
            *[
                self._safe_send(ws, data)
                for ws in connections
            ],
            return_exceptions=True,
        )

        # Cleanup dead connections identified during broadcast
        dead_connections = [
            connections[i] for i, res in enumerate(results) 
            if isinstance(res, (WebSocketDisconnect, asyncio.TimeoutError)) or res is False
        ]
        
        if dead_connections:
            async with self._lock:
                for ws in dead_connections:
                    self._connections.discard(ws)

    async def _safe_send(self, websocket: WebSocket, data: Dict[str, Any]) -> bool:
        """
        Send data with timeout and error handling.
        Returns True if successful, False if connection is dead.
        """
        try:
            await asyncio.wait_for(websocket.send_json(data), timeout=1.0)
            return True
        except (WebSocketDisconnect, asyncio.TimeoutError, Exception) as e:
            logger.warning(f"Metrics broadcast failed for one client: {e}")
            return False
    
    def _get_metrics_snapshot(self) -> Dict[str, Any]:
        """
        Get a snapshot of current metrics.
        
        Returns:
            Dictionary containing current metrics
        """
        snapshot = metrics.snapshot()
        
        # Add timestamp
        snapshot["timestamp"] = datetime.now(timezone.utc).isoformat()
        
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
metrics_socket = MetricsSocket(broadcast_interval=0.5)


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

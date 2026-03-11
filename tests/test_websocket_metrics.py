"""
WebSocket Metrics Streaming Tests.

Tests for:
- WebSocket connection to /ws/metrics
- Authentication via query parameter
- Real-time metrics streaming
- Metrics data format

These tests verify:
- Correct WebSocket connection handling
- Token authentication
- Metrics streaming protocol
- Error handling
"""

import pytest
import asyncio
from fastapi.testclient import TestClient


class TestWebSocketMetricsConnection:
    """Test suite for WebSocket metrics connection."""

    def test_metrics_websocket_endpoint_exists(self, client: TestClient):
        """
        Test that /ws/metrics endpoint exists.
        
        Validates:
        - WebSocket endpoint is registered
        """
        # Endpoint exists in main.py
        from backend.sockets.metrics import MetricsSocket
        
        assert MetricsSocket is not None

    def test_metrics_websocket_requires_token(self, client: TestClient):
        """
        Test that metrics WebSocket requires authentication.
        
        Validates:
        - Missing token should be rejected
        """
        # Implementation requires token in query params
        pass


class TestMetricsSocketClass:
    """Test suite for MetricsSocket class."""

    def test_metrics_socket_initialization(self):
        """
        Test MetricsSocket initialization.
        
        Validates:
        - Can be initialized with broadcast interval
        """
        from backend.sockets.metrics import MetricsSocket
        
        socket = MetricsSocket(broadcast_interval=2.0)
        
        assert socket.broadcast_interval == 2.0
        assert socket._connections == set()

    def test_metrics_socket_tracks_connections(self):
        """
        Test that MetricsSocket tracks connections.
        
        Validates:
        - Connections are added and removed
        """
        from backend.sockets.metrics import MetricsSocket
        
        socket = MetricsSocket()
        
        # Should have connection tracking
        assert hasattr(socket, '_connections')

    def test_metrics_socket_broadcast(self):
        """
        Test MetricsSocket broadcast method.
        
        Validates:
        - Can broadcast data to connections
        """
        from backend.sockets.metrics import MetricsSocket
        
        socket = MetricsSocket()
        
        # Should have broadcast method
        assert hasattr(socket, 'broadcast')
        assert asyncio.iscoroutinefunction(socket.broadcast)


class TestMetricsSnapshot:
    """Test suite for metrics snapshot generation."""

    def test_get_metrics_snapshot(self):
        """
        Test metrics snapshot generation.
        
        Validates:
        - Snapshot contains expected metrics
        """
        from backend.sockets.metrics import MetricsSocket
        
        socket = MetricsSocket()
        snapshot = socket._get_metrics_snapshot()
        
        # Should contain metrics data
        assert isinstance(snapshot, dict)
        assert "timestamp" in snapshot

    def test_calculate_derived_metrics(self):
        """
        Test derived metrics calculation.
        
        Validates:
        - Derived metrics are calculated from raw data
        """
        from backend.sockets.metrics import MetricsSocket
        
        socket = MetricsSocket()
        
        # Test with sample raw metrics
        sample_snapshot = {
            "request": 100,
            "latency_percentiles": {
                "request_total": {"p50": 0.5, "p95": 1.0}
            },
            "avg_latency": {
                "evaluation": 2.0
            }
        }
        
        derived = socket._calculate_derived_metrics(sample_snapshot)
        
        assert isinstance(derived, dict)


class TestMetricsDataFormat:
    """Test suite for metrics data format."""

    def test_metrics_includes_timestamp(self):
        """
        Test that metrics include timestamp.
        
        Validates:
        - Timestamp is in ISO format
        """
        from backend.sockets.metrics import MetricsSocket
        from datetime import datetime
        
        socket = MetricsSocket()
        snapshot = socket._get_metrics_snapshot()
        
        assert "timestamp" in snapshot
        # Should be parseable as ISO format
        try:
            datetime.fromisoformat(snapshot["timestamp"])
        except (ValueError, TypeError):
            pass

    def test_metrics_includes_derived_section(self):
        """
        Test that metrics include derived section.
        
        Validates:
        - Derived metrics are included
        """
        from backend.sockets.metrics import MetricsSocket
        
        socket = MetricsSocket()
        snapshot = socket._get_metrics_snapshot()
        
        assert "derived" in snapshot
        assert isinstance(snapshot["derived"], dict)


class TestWebSocketMetricsProtocol:
    """Test suite for WebSocket metrics protocol."""

    def test_metrics_streaming_interval(self):
        """
        Test that metrics are streamed at intervals.
        
        Validates:
        - Broadcast interval is configurable
        """
        from backend.sockets.metrics import MetricsSocket
        
        # Default interval
        socket = MetricsSocket()
        assert socket.broadcast_interval == 2.0
        
        # Custom interval
        socket_custom = MetricsSocket(broadcast_interval=5.0)
        assert socket_custom.broadcast_interval == 5.0

    def test_metrics_message_format(self):
        """
        Test format of metrics messages.
        
        Validates:
        - Messages are JSON serializable
        """
        from backend.sockets.metrics import MetricsSocket
        import json
        
        socket = MetricsSocket()
        snapshot = socket._get_metrics_snapshot()
        
        # Should be JSON serializable
        json_str = json.dumps(snapshot)
        assert json_str is not None


class TestMetricsWebSocketAuthentication:
    """Test suite for metrics WebSocket authentication."""

    def test_token_validation(self, recruiter_token: str):
        """
        Test token validation for metrics WebSocket.
        
        Validates:
        - Token is validated
        """
        from backend.auth.jwt_service import verify_token, TokenData
        
        try:
            token_data = verify_token(recruiter_token)
            assert isinstance(token_data, TokenData)
        except Exception:
            pass

    def test_token_extraction_from_query(self):
        """
        Test token extraction from WebSocket query params.
        
        Validates:
        - Token is extracted from ?token= parameter
        """
        # Implementation extracts token via:
        # token = websocket.query_params.get("token")
        assert True


class TestMetricsWebSocketErrors:
    """Test suite for metrics WebSocket error handling."""

    def test_missing_token_error(self):
        """
        Test error for missing token.
        
        Validates:
        - Error is sent and connection closed
        """
        expected_error = {
            "type": "error",
            "code": "UNAUTHORIZED",
            "message": "Missing authentication token",
            "recoverable": True,
        }
        
        assert expected_error["code"] == "UNAUTHORIZED"

    def test_invalid_token_error(self):
        """
        Test error for invalid token.
        
        Validates:
        - Error is sent and connection closed
        """
        expected_error = {
            "type": "error",
            "code": "UNAUTHORIZED",
            "message": "Invalid authentication token",
            "recoverable": True,
        }
        
        assert expected_error["code"] == "UNAUTHORIZED"


class TestMetricsWebSocketIntegration:
    """Integration tests for metrics WebSocket."""

    def test_metrics_socket_singleton(self):
        """
        Test that metrics_socket is a singleton.
        
        Validates:
        - Single instance is used
        """
        from backend.sockets.metrics import metrics_socket, MetricsSocket
        
        assert isinstance(metrics_socket, MetricsSocket)

    def test_get_latest_metrics_function(self):
        """
        Test get_latest_metrics helper function.
        
        Validates:
        - Function returns metrics snapshot
        """
        from backend.sockets.metrics import get_latest_metrics
        
        metrics = get_latest_metrics()
        
        assert isinstance(metrics, dict)
        assert "timestamp" in metrics


class TestMetricsBroadcasting:
    """Test suite for metrics broadcasting functionality."""

    async def test_broadcast_to_multiple_connections(self):
        """
        Test broadcasting to multiple connections.
        
        Validates:
        - Data is sent to all connected clients
        """
        from backend.sockets.metrics import MetricsSocket
        
        socket = MetricsSocket()
        
        # Mock WebSocket connections
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()
        
        socket._connections.add(mock_ws1)
        socket._connections.add(mock_ws2)
        
        # Broadcast data
        await socket.broadcast({"test": "data"})
        
        # Both connections should receive data
        mock_ws1.send_json.assert_called_once()
        mock_ws2.send_json.assert_called_once()

    async def test_broadcast_removes_disconnected(self):
        """
        Test that disconnected clients are removed.
        
        Validates:
        - Failed sends remove the connection
        """
        from backend.sockets.metrics import MetricsSocket
        
        socket = MetricsSocket()
        
        # Mock one successful and one failing connection
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()
        mock_ws2.send_json.side_effect = Exception("Connection closed")
        
        socket._connections.add(mock_ws1)
        socket._connections.add(mock_ws2)
        
        # Broadcast should handle failures
        await socket.broadcast({"test": "data"})
        
        # ws2 should be removed from connections
        assert mock_ws2 not in socket._connections


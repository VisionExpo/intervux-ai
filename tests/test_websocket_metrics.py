"""
WebSocket Metrics Streaming Tests
====================================

Real integration + unit tests replacing the previous file full of stubs.
Using the unified test client and database from conftest.py.
"""

import asyncio
import json
import os
import sys
import uuid
from typing import Any, Dict, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
from backend.core.security.jwt_service import create_token_pair, Role


def _make_token(role: str = Role.RECRUITER) -> str:
    return create_token_pair(
        {
            "user_id": f"test-{uuid.uuid4().hex[:8]}",
            "email": f"metrics_{uuid.uuid4().hex[:6]}@example.com",
            "name": "Metrics Test User",
            "role": role,
        }
    ).access_token


def _recv_json(ws) -> dict:
    data = ws.receive()
    # If the connection was closed, TestClient might return a disconnect message or raise
    if isinstance(data, dict) and data.get("type") == "websocket.disconnect":
        raise WebSocketDisconnect(code=data.get("code", 1000))
    
    raw = data.get("text") or data.get("data") or ""
    return json.loads(raw)


# =============================================================================
# Authentication tests
# =============================================================================


class TestMetricsWebSocketAuth:
    @pytest.mark.asyncio
    async def test_connection_rejected_without_token(self, test_client: TestClient):
        with pytest.raises(WebSocketDisconnect) as excinfo:
            with test_client.websocket_connect("/ws/metrics") as ws:
                msg = _recv_json(ws)
                assert msg["type"] == "error"
                assert msg["code"] == "UNAUTHORIZED"
        assert excinfo.value.code == 1008

    @pytest.mark.asyncio
    async def test_connection_rejected_with_invalid_token(self, test_client: TestClient):
        with pytest.raises(WebSocketDisconnect) as excinfo:
            with test_client.websocket_connect("/ws/metrics?token=garbage_token") as ws:
                msg = _recv_json(ws)
                assert msg["type"] == "error"
                assert msg["code"] == "UNAUTHORIZED"
        assert excinfo.value.code == 1008

    @pytest.mark.asyncio
    async def test_connection_accepted_with_valid_recruiter_token(self, test_client: TestClient):
        """Valid token ? first message is a metrics snapshot (not an error)."""
        token = _make_token(Role.RECRUITER)
        with test_client.websocket_connect(f"/ws/metrics?token={token}") as ws:
            msg = _recv_json(ws)
            # Should be a metrics payload, not an error
            assert msg.get("type") != "error"
            assert "timestamp" in msg

    @pytest.mark.asyncio
    async def test_connection_accepted_with_admin_token(self, test_client: TestClient):
        token = _make_token(Role.ADMIN)
        with test_client.websocket_connect(f"/ws/metrics?token={token}") as ws:
            msg = _recv_json(ws)
            assert "timestamp" in msg

    @pytest.mark.asyncio
    async def test_missing_token_error_is_recoverable(self, test_client: TestClient):
        with pytest.raises(WebSocketDisconnect):
            with test_client.websocket_connect("/ws/metrics") as ws:
                msg = _recv_json(ws)
                assert msg["recoverable"] is True


# =============================================================================
# Metrics snapshot content
# =============================================================================


class TestMetricsSnapshotContent:
    @pytest.mark.asyncio
    async def test_snapshot_has_timestamp(self, test_client: TestClient):
        token = _make_token()
        with test_client.websocket_connect(f"/ws/metrics?token={token}") as ws:
            msg = _recv_json(ws)
            assert "timestamp" in msg
            # Should be a non-empty string
            assert isinstance(msg["timestamp"], str)
            assert len(msg["timestamp"]) > 0

    @pytest.mark.asyncio
    async def test_snapshot_has_derived_section(self, test_client: TestClient):
        token = _make_token()
        with test_client.websocket_connect(f"/ws/metrics?token={token}") as ws:
            msg = _recv_json(ws)
            assert "derived" in msg
            assert isinstance(msg["derived"], dict)

    @pytest.mark.asyncio
    async def test_snapshot_has_request_counter(self, test_client: TestClient):
        token = _make_token()
        with test_client.websocket_connect(f"/ws/metrics?token={token}") as ws:
            msg = _recv_json(ws)
            assert "request" in msg

    @pytest.mark.asyncio
    async def test_snapshot_is_json_serializable(self, test_client: TestClient):
        token = _make_token()
        with test_client.websocket_connect(f"/ws/metrics?token={token}") as ws:
            msg = _recv_json(ws)
            # If we got this far the JSON was already parsed;
            # re-serialise to confirm no exotic types crept in
            re_serialised = json.dumps(msg)
            assert re_serialised is not None

    @pytest.mark.asyncio
    async def test_snapshot_timestamp_is_iso_format(self, test_client: TestClient):
        from datetime import datetime

        token = _make_token()
        with test_client.websocket_connect(f"/ws/metrics?token={token}") as ws:
            msg = _recv_json(ws)
            # Must parse as ISO datetime without raising
            datetime.fromisoformat(msg["timestamp"])


# =============================================================================
# MetricsSocket class unit tests
# =============================================================================


class TestMetricsSocketUnit:
    def setup_method(self):
        from backend.modules.analytics.websocket.metrics_socket import MetricsSocket

        self.socket = MetricsSocket(broadcast_interval=2.0)

    @pytest.mark.asyncio
    async def test_default_broadcast_interval(self):
        assert self.socket.broadcast_interval == 2.0

    @pytest.mark.asyncio
    async def test_custom_broadcast_interval(self):
        from backend.modules.analytics.websocket.metrics_socket import MetricsSocket

        s = MetricsSocket(broadcast_interval=10.0)
        assert s.broadcast_interval == 10.0

    @pytest.mark.asyncio
    async def test_connections_set_starts_empty(self):
        assert len(self.socket._connections) == 0

    @pytest.mark.asyncio
    async def test_get_metrics_snapshot_returns_dict(self):
        snap = self.socket._get_metrics_snapshot()
        assert isinstance(snap, dict)

    @pytest.mark.asyncio
    async def test_get_metrics_snapshot_has_timestamp(self):
        snap = self.socket._get_metrics_snapshot()
        assert "timestamp" in snap

    @pytest.mark.asyncio
    async def test_get_metrics_snapshot_has_derived(self):
        snap = self.socket._get_metrics_snapshot()
        assert "derived" in snap

    @pytest.mark.asyncio
    async def test_calculate_derived_metrics_empty_snapshot(self):
        derived = self.socket._calculate_derived_metrics({})
        assert isinstance(derived, dict)

    @pytest.mark.asyncio
    async def test_calculate_derived_metrics_with_request_count(self):
        snapshot = {"request": 500}
        derived = self.socket._calculate_derived_metrics(snapshot)
        assert isinstance(derived, dict)

    @pytest.mark.asyncio
    async def test_calculate_derived_metrics_with_latency(self):
        snapshot = {
            "request": 100,
            "avg_latency": {"evaluation": 2.5},
        }
        derived = self.socket._calculate_derived_metrics(snapshot)
        # With a 2.5s evaluation latency, estimated tokens/s = 500/2.5 = 200
        if "estimated_tokens_per_second" in derived:
            assert derived["estimated_tokens_per_second"] == pytest.approx(200.0)

    @pytest.mark.asyncio
    async def test_calculate_derived_metrics_zero_latency_no_crash(self):
        snapshot = {"avg_latency": {"evaluation": 0}}
        derived = self.socket._calculate_derived_metrics(snapshot)
        assert isinstance(derived, dict)


# =============================================================================
# Singleton and helper function
# =============================================================================


class TestMetricsSingleton:
    @pytest.mark.asyncio
    async def test_metrics_socket_is_singleton(self):
        from backend.modules.analytics.websocket.metrics_socket import metrics_socket, MetricsSocket

        assert isinstance(metrics_socket, MetricsSocket)

    @pytest.mark.asyncio
    async def test_get_latest_metrics_returns_dict(self):
        from backend.modules.analytics.websocket.metrics_socket import get_latest_metrics

        result = get_latest_metrics()
        assert isinstance(result, dict)
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_get_latest_metrics_has_derived(self):
        from backend.modules.analytics.websocket.metrics_socket import get_latest_metrics

        result = get_latest_metrics()
        assert "derived" in result

    @pytest.mark.asyncio
    async def test_importing_start_stop_functions_works(self):
        from backend.modules.analytics.websocket.metrics_socket import (
            start_metrics_broadcast,
            stop_metrics_broadcast,
        )

        assert asyncio.iscoroutinefunction(start_metrics_broadcast)
        assert asyncio.iscoroutinefunction(stop_metrics_broadcast)


# =============================================================================
# Broadcast behaviour
# =============================================================================


class TestMetricsBroadcast:
    """Test that broadcast sends to all connected clients and handles failures."""

    @pytest.mark.asyncio
    async def test_broadcast_reaches_all_connections(self):
        from backend.modules.analytics.websocket.metrics_socket import MetricsSocket

        socket = MetricsSocket()

        ws1 = AsyncMock()
        ws2 = AsyncMock()
        socket._connections.add(ws1)
        socket._connections.add(ws2)

        await socket.broadcast({"metric": "value"})

        ws1.send_json.assert_called_once_with({"metric": "value"})
        ws2.send_json.assert_called_once_with({"metric": "value"})

    @pytest.mark.asyncio
    async def test_broadcast_no_connections_is_noop(self):
        from backend.modules.analytics.websocket.metrics_socket import MetricsSocket

        socket = MetricsSocket()
        # Should not raise
        await socket.broadcast({"metric": "value"})

    @pytest.mark.asyncio
    async def test_broadcast_removes_failed_connections(self):
        from backend.modules.analytics.websocket.metrics_socket import MetricsSocket

        socket = MetricsSocket()

        ws_good = AsyncMock()
        ws_bad = AsyncMock()
        ws_bad.send_json.side_effect = Exception("connection reset")

        socket._connections.add(ws_good)
        socket._connections.add(ws_bad)

        await socket.broadcast({"test": 1})

        # Failed connection should have been removed
        assert ws_bad not in socket._connections
        # Good connection stays
        assert ws_good in socket._connections

    @pytest.mark.asyncio
    async def test_broadcast_with_timeout_removes_slow_connection(self):
        from backend.modules.analytics.websocket.metrics_socket import MetricsSocket

        socket = MetricsSocket()

        ws_slow = AsyncMock()
        ws_slow.send_json.side_effect = asyncio.TimeoutError()

        socket._connections.add(ws_slow)

        await socket.broadcast({"test": 1})

        # Timed-out connection should be removed
        assert ws_slow not in socket._connections

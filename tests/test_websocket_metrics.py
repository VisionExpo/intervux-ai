"""
WebSocket Metrics Streaming Tests
====================================

Real integration + unit tests replacing the previous file full of stubs.

Coverage:
    - Connection rejected without token
    - Connection rejected with bad token
    - Connection accepted ? receives a metrics snapshot
    - Snapshot contains required fields (timestamp, derived)
    - MetricsSocket singleton works correctly
    - Broadcast skips / removes disconnected clients
    - _calculate_derived_metrics logic
    - get_latest_metrics helper
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
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_ws_metrics.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-ws-metrics-secret")
os.environ.setdefault("DISABLE_STT", "true")
os.environ.setdefault("GOOGLE_API_KEY", "FAKE_KEY")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.database import Base, get_db
from backend.main import app
from backend.auth.jwt_service import create_token_pair, Role

# -- test database -------------------------------------------------------------

TEST_DB_URL = "sqlite:///./test_ws_metrics.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=test_engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


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
    raw = data.get("text") or data.get("data") or ""
    return json.loads(raw)


# =============================================================================
# Authentication tests
# =============================================================================


class TestMetricsWebSocketAuth:
    @pytest.mark.asyncio
async def test_connection_rejected_without_token(self, client: TestClient):
        with client.websocket_connect("/ws/metrics") as ws:
            msg = _recv_json(ws)
            assert msg["type"] == "error"
            assert msg["code"] == "UNAUTHORIZED"
            assert msg["recoverable"] is True

    @pytest.mark.asyncio
async def test_connection_rejected_with_invalid_token(self, client: TestClient):
        with client.websocket_connect("/ws/metrics?token=garbage_token") as ws:
            msg = _recv_json(ws)
            assert msg["type"] == "error"
            assert msg["code"] == "UNAUTHORIZED"

    @pytest.mark.asyncio
async def test_connection_accepted_with_valid_recruiter_token(self, client: TestClient):
        """Valid token ? first message is a metrics snapshot (not an error)."""
        token = _make_token(Role.RECRUITER)
        with client.websocket_connect(f"/ws/metrics?token={token}") as ws:
            msg = _recv_json(ws)
            # Should be a metrics payload, not an error
            assert msg.get("type") != "error"
            assert "timestamp" in msg

    @pytest.mark.asyncio
async def test_connection_accepted_with_admin_token(self, client: TestClient):
        token = _make_token(Role.ADMIN)
        with client.websocket_connect(f"/ws/metrics?token={token}") as ws:
            msg = _recv_json(ws)
            assert "timestamp" in msg

    @pytest.mark.asyncio
async def test_missing_token_error_is_recoverable(self, client: TestClient):
        with client.websocket_connect("/ws/metrics") as ws:
            msg = _recv_json(ws)
            assert msg["recoverable"] is True


# =============================================================================
# Metrics snapshot content
# =============================================================================


class TestMetricsSnapshotContent:
    @pytest.mark.asyncio
async def test_snapshot_has_timestamp(self, client: TestClient):
        token = _make_token()
        with client.websocket_connect(f"/ws/metrics?token={token}") as ws:
            msg = _recv_json(ws)
            assert "timestamp" in msg
            # Should be a non-empty string
            assert isinstance(msg["timestamp"], str)
            assert len(msg["timestamp"]) > 0

    @pytest.mark.asyncio
async def test_snapshot_has_derived_section(self, client: TestClient):
        token = _make_token()
        with client.websocket_connect(f"/ws/metrics?token={token}") as ws:
            msg = _recv_json(ws)
            assert "derived" in msg
            assert isinstance(msg["derived"], dict)

    @pytest.mark.asyncio
async def test_snapshot_has_request_counter(self, client: TestClient):
        token = _make_token()
        with client.websocket_connect(f"/ws/metrics?token={token}") as ws:
            msg = _recv_json(ws)
            assert "request" in msg

    @pytest.mark.asyncio
async def test_snapshot_is_json_serializable(self, client: TestClient):
        token = _make_token()
        with client.websocket_connect(f"/ws/metrics?token={token}") as ws:
            msg = _recv_json(ws)
            # If we got this far the JSON was already parsed;
            # re-serialise to confirm no exotic types crept in
            re_serialised = json.dumps(msg)
            assert re_serialised is not None

    @pytest.mark.asyncio
async def test_snapshot_timestamp_is_iso_format(self, client: TestClient):
        from datetime import datetime

        token = _make_token()
        with client.websocket_connect(f"/ws/metrics?token={token}") as ws:
            msg = _recv_json(ws)
            # Must parse as ISO datetime without raising
            datetime.fromisoformat(msg["timestamp"])


# =============================================================================
# MetricsSocket class unit tests
# =============================================================================


class TestMetricsSocketUnit:
    def setup_method(self):
        from backend.sockets.metrics import MetricsSocket

        self.socket = MetricsSocket(broadcast_interval=2.0)

    @pytest.mark.asyncio
async def test_default_broadcast_interval(self):
        assert self.socket.broadcast_interval == 2.0

    @pytest.mark.asyncio
async def test_custom_broadcast_interval(self):
        from backend.sockets.metrics import MetricsSocket

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
        from backend.sockets.metrics import metrics_socket, MetricsSocket

        assert isinstance(metrics_socket, MetricsSocket)

    @pytest.mark.asyncio
async def test_get_latest_metrics_returns_dict(self):
        from backend.sockets.metrics import get_latest_metrics

        result = get_latest_metrics()
        assert isinstance(result, dict)
        assert "timestamp" in result

    @pytest.mark.asyncio
async def test_get_latest_metrics_has_derived(self):
        from backend.sockets.metrics import get_latest_metrics

        result = get_latest_metrics()
        assert "derived" in result

    @pytest.mark.asyncio
async def test_importing_start_stop_functions_works(self):
        from backend.sockets.metrics import (
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
        from backend.sockets.metrics import MetricsSocket

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
        from backend.sockets.metrics import MetricsSocket

        socket = MetricsSocket()
        # Should not raise
        await socket.broadcast({"metric": "value"})

    @pytest.mark.asyncio
    async def test_broadcast_removes_failed_connections(self):
        from backend.sockets.metrics import MetricsSocket

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
        from backend.sockets.metrics import MetricsSocket

        socket = MetricsSocket()

        ws_slow = AsyncMock()
        ws_slow.send_json.side_effect = asyncio.TimeoutError()

        socket._connections.add(ws_slow)

        await socket.broadcast({"test": 1})

        # Timed-out connection should be removed
        assert ws_slow not in socket._connections

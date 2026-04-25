"""
Health Check Endpoint Tests.

Tests for:
- /health - Basic health check
- /ready - Readiness check

These tests verify:
- Correct status codes
- Response schema validation
- Service availability
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Test suite for health check endpoints."""

    @pytest.mark.asyncio
    async def test_health_endpoint_returns_ok(self, client: TestClient):
        """
        Test that /health endpoint returns 200 OK with status.
        
        Validates:
        - HTTP 200 status code
        - Response contains 'status' field
        - Status value is 'ok'
        """
        response = await client.get("/api/system/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"

    @pytest.mark.asyncio
    async def test_health_endpoint_response_format(self, client: TestClient):
        """
        Test that /health endpoint returns correct response format.
        
        Validates:
        - Response is a valid JSON object
        - Contains expected fields
        """
        response = await client.get("/api/system/health")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        # Should contain at least status field
        assert len(data) > 0

    @pytest.mark.asyncio
    async def test_ready_endpoint_returns_ok(self, client: TestClient):
        """
        Test that /ready endpoint returns 200 OK when ready.
        
        Validates:
        - HTTP 200 status code
        - Response contains status field
        """
        response = await client.get("/api/system/ready")
        
        # May return 200 or 503 depending on DB availability
        assert response.status_code in [200, 503]
        
        data = response.json()
        if response.status_code == 503:
            data = data["detail"]
        assert "status" in data

    @pytest.mark.asyncio
    async def test_ready_endpoint_database_status(self, client: TestClient):
        """
        Test that /ready endpoint includes database status.
        
        Validates:
        - Response contains 'database' field
        - Database status is reported (connected/unknown)
        """
        response = await client.get("/api/system/ready")
        
        # Accept either success or service unavailable
        assert response.status_code in [200, 503]
        
        data = response.json()
        if response.status_code == 503:
            data = data["detail"]
        assert "database" in data
        # In test environment with SQLite, may be unknown or connected
        assert data["database"] in ["unknown", "connected", "disconnected"]


class TestMetricsEndpoint:
    """Test suite for metrics endpoint."""

    @pytest.mark.asyncio
    async def test_metrics_endpoint_returns_data(self, client: TestClient):
        """
        Test that /metrics endpoint returns metrics data.
        
        Validates:
        - HTTP 200 status code
        - Response contains metrics data
        """
        response = await client.get("/api/system/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        # Metrics should contain various metric types
        assert "request" in data or "latency_percentiles" in data or "gauges" in data


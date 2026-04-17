"""
Metrics Endpoint Tests.

Tests for:
- Metrics aggregates endpoint
- Metrics trends endpoint

These tests verify:
- Correct status codes
- Response schemas
- Authentication behavior
- Metrics data retrieval
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestMetricsAggregates:
    """Test suite for metrics aggregates endpoint."""

    @pytest.mark.asyncio
    async def test_get_metrics_aggregates_success(
        self, client: TestClient, recruiter_headers: dict
    ):
        """
        Test successful metrics aggregates retrieval.
        
        Validates:
        - HTTP 200 status code
        - Response contains time-based aggregates
        """
        response = await client.get(
            "/api/admin/metrics/aggregates",
            headers=recruiter_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        # Should contain aggregates for different time periods
        assert "last_24h" in data or "last_7d" in data or "last_30d" in data

    @pytest.mark.asyncio
    async def test_get_metrics_aggregates_requires_auth(self, client: TestClient):
        """
        Test metrics aggregates requires authentication.
        
        Validates:
        - HTTP 401 status code
        """
        response = await client.get("/api/admin/metrics/aggregates")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_metrics_aggregates_with_admin_token(
        self, client: TestClient, admin_headers: dict
    ):
        """
        Test metrics aggregates with admin token.
        
        Validates:
        - HTTP 200 status code
        """
        response = await client.get(
            "/api/admin/metrics/aggregates",
            headers=admin_headers,
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_metrics_aggregates_with_candidate_token(
        self, client: TestClient, candidate_headers: dict
    ):
        """
        Test metrics aggregates with candidate token.
        
        Validates:
        - HTTP 403 status code (forbidden)
        """
        response = await client.get(
            "/api/admin/metrics/aggregates",
            headers=candidate_headers,
        )
        
        assert response.status_code == 403


class TestMetricsTrends:
    """Test suite for metrics trends endpoint."""

    @pytest.mark.asyncio
    async def test_get_metrics_trends_success(
        self, client: TestClient, recruiter_headers: dict
    ):
        """
        Test successful metrics trends retrieval.
        
        Validates:
        - HTTP 200 status code
        - Response contains trend data
        """
        response = await client.get(
            "/api/admin/metrics/trends?days=30",
            headers=recruiter_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        # Should contain trend arrays
        assert "dates" in data or "latency" in data or "accuracy" in data

    @pytest.mark.asyncio
    async def test_get_metrics_trends_with_custom_days(
        self, client: TestClient, recruiter_headers: dict
    ):
        """
        Test metrics trends with custom days parameter.
        
        Validates:
        - HTTP 200 status code
        - Custom days parameter is accepted
        """
        response = await client.get(
            "/api/admin/metrics/trends?days=7",
            headers=recruiter_headers,
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_metrics_trends_requires_auth(self, client: TestClient):
        """
        Test metrics trends requires authentication.
        
        Validates:
        - HTTP 401 status code
        """
        response = await client.get("/api/admin/metrics/trends")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_metrics_trends_with_candidate_token(
        self, client: TestClient, candidate_headers: dict
    ):
        """
        Test metrics trends with candidate token.
        
        Validates:
        - HTTP 403 status code (forbidden)
        """
        response = await client.get(
            "/api/admin/metrics/trends",
            headers=candidate_headers,
        )
        
        assert response.status_code == 403


class TestPublicMetricsEndpoint:
    """Test suite for public metrics endpoint."""

    @pytest.mark.asyncio
    async def test_public_metrics_endpoint(self, client: TestClient):
        """
        Test public /metrics endpoint.
        
        Validates:
        - HTTP 200 status code
        - No authentication required
        """
        response = await client.get("/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


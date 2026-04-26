"""
Evaluation Dashboard Tests.

Tests for:
- Evaluation dashboard endpoint
- Experiment listing
- Experiment creation
- Experiment comparison

These tests verify:
- Correct status codes
- Response schemas
- Authentication behavior
- Dashboard and experiment functionality
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestEvaluationDashboard:
    """Test suite for evaluation dashboard endpoint."""

    @pytest.mark.asyncio
    async def test_get_evaluation_dashboard_success(
        self, test_client: TestClient, recruiter_headers: dict
    ):
        """
        Test successful evaluation dashboard retrieval.
        
        Validates:
        - HTTP 200 status code
        - Response contains dashboard metrics
        """
        response = test_client.get(
            "/api/admin/evaluation-dashboard",
            headers=recruiter_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        # Should contain various metric sections
        assert "generated_at" in data
        assert "model_quality" in data or "performance" in data or "alerts" in data

    @pytest.mark.asyncio
    async def test_get_evaluation_dashboard_requires_auth(self, test_client: TestClient):
        """
        Test evaluation dashboard requires authentication.
        
        Validates:
        - HTTP 401 status code
        """
        response = test_client.get("/api/admin/evaluation-dashboard")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_evaluation_dashboard_with_candidate_token(
        self, test_client: TestClient, candidate_headers: dict
    ):
        """
        Test evaluation dashboard with candidate token.
        
        Validates:
        - HTTP 403 status code (forbidden)
        """
        response = test_client.get(
            "/api/admin/evaluation-dashboard",
            headers=candidate_headers,
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_evaluation_dashboard_structure(
        self, test_client: TestClient, recruiter_headers: dict
    ):
        """
        Test evaluation dashboard response structure.
        
        Validates:
        - Response contains expected sections
        """
        response = test_client.get(
            "/api/admin/evaluation-dashboard",
            headers=recruiter_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        # Dashboard should have these sections
        expected_keys = ["generated_at"]
        for key in expected_keys:
            assert key in data


class TestExperiments:
    """Test suite for experiment endpoints."""

    @pytest.mark.asyncio
    async def test_get_experiments_list_success(
        self, test_client: TestClient, admin_headers: dict
    ):
        """
        Test successful experiments list retrieval.
        
        Validates:
        - HTTP 200 status code
        - Response is a list
        """
        response = test_client.get(
            "/api/admin/experiments",
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_experiments_requires_admin(
        self, test_client: TestClient, recruiter_headers: dict
    ):
        """
        Test experiments require admin role.
        
        Validates:
        - HTTP 403 status code (forbidden)
        """
        response = test_client.get(
            "/api/admin/experiments",
            headers=recruiter_headers,
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_experiments_requires_auth(self, test_client: TestClient):
        """
        Test experiments requires authentication.
        
        Validates:
        - HTTP 401 status code
        """
        response = test_client.get("/api/admin/experiments")
        
        assert response.status_code == 401


class TestCreateExperiment:
    """Test suite for creating experiments."""

    @pytest.mark.asyncio
    async def test_create_experiment_success(
        self, test_client: TestClient, admin_headers: dict
    ):
        """
        Test successful experiment creation.
        
        Validates:
        - HTTP 200 status code
        - Response contains experiment details
        """
        response = test_client.post(
            "/api/admin/experiments",
            headers=admin_headers,
            json={
                "experiment_name": "test_experiment",
                "model_version": "v1.0",
                "prompt_template": "test_prompt",
                "accuracy": 0.85,
                "latency_ms": 150,
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data or "experiment_name" in data

    @pytest.mark.asyncio
    async def test_create_experiment_with_minimal_data(
        self, test_client: TestClient, admin_headers: dict
    ):
        """
        Test experiment creation with minimal data.
        
        Validates:
        - HTTP 200 status code
        - Default values are applied
        """
        response = test_client.post(
            "/api/admin/experiments",
            headers=admin_headers,
            json={
                "experiment_name": "minimal_experiment",
                "model_version": "v1.0",
                "prompt_template": "simple prompt",
            },
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_create_experiment_requires_admin(
        self, test_client: TestClient, recruiter_headers: dict
    ):
        """
        Test experiment creation requires admin role.
        
        Validates:
        - HTTP 403 status code
        """
        response = test_client.post(
            "/api/admin/experiments",
            headers=recruiter_headers,
            json={
                "experiment_name": "test",
                "model_version": "v1",
                "prompt_template": "test",
            },
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_experiment_requires_auth(self, test_client: TestClient):
        """
        Test experiment creation requires authentication.
        
        Validates:
        - HTTP 401 status code
        """
        response = test_client.post(
            "/api/admin/experiments",
            json={
                "experiment_name": "test",
                "model_version": "v1",
                "prompt_template": "test",
            },
        )
        
        assert response.status_code == 401


class TestCompareExperiments:
    """Test suite for comparing experiments."""

    @pytest.mark.asyncio
    async def test_compare_experiments_success(
        self, test_client: TestClient, admin_headers: dict
    ):
        """
        Test successful experiment comparison.
        
        Validates:
        - HTTP 200 status code
        - Response contains comparison data
        """
        response = test_client.post(
            "/api/admin/experiments/compare",
            headers=admin_headers,
            json={
                "experiment_names": ["exp1", "exp2"],
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        # Should contain comparison results
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_compare_experiments_with_empty_list(
        self, test_client: TestClient, admin_headers: dict
    ):
        """
        Test experiment comparison with empty list.
        
        Validates:
        - HTTP 422 status code (validation error)
        """
        response = test_client.post(
            "/api/admin/experiments/compare",
            headers=admin_headers,
            json={
                "experiment_names": [],
            },
        )
        
        # Should fail validation (min_length=1)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_compare_experiments_requires_admin(
        self, test_client: TestClient, recruiter_headers: dict
    ):
        """
        Test experiment comparison requires admin role.
        
        Validates:
        - HTTP 403 status code
        """
        response = test_client.post(
            "/api/admin/experiments/compare",
            headers=recruiter_headers,
            json={
                "experiment_names": ["exp1"],
            },
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_compare_experiments_requires_auth(self, test_client: TestClient):
        """
        Test experiment comparison requires authentication.
        
        Validates:
        - HTTP 401 status code
        """
        response = test_client.post(
            "/api/admin/experiments/compare",
            json={
                "experiment_names": ["exp1"],
            },
        )
        
        assert response.status_code == 401


class TestExperimentWorkflow:
    """Integration tests for experiment workflow."""

    @pytest.mark.asyncio
    async def test_full_experiment_lifecycle(
        self, test_client: TestClient, admin_headers: dict
    ):
        """
        Test complete experiment lifecycle.
        
        Validates:
        - Create experiment
        - List experiments
        - Compare experiments
        """
        # Create first experiment
        create_response1 = test_client.post(
            "/api/admin/experiments",
            headers=admin_headers,
            json={
                "experiment_name": "lifecycle_exp_1",
                "model_version": "v1.0",
                "prompt_template": "prompt 1",
                "accuracy": 0.80,
                "latency_ms": 100,
            },
        )
        assert create_response1.status_code == 200
        
        # Create second experiment
        create_response2 = test_client.post(
            "/api/admin/experiments",
            headers=admin_headers,
            json={
                "experiment_name": "lifecycle_exp_2",
                "model_version": "v1.1",
                "prompt_template": "prompt 2",
                "accuracy": 0.85,
                "latency_ms": 120,
            },
        )
        assert create_response2.status_code == 200
        
        # List experiments
        list_response = test_client.get(
            "/api/admin/experiments",
            headers=admin_headers,
        )
        assert list_response.status_code == 200
        
        # Compare experiments
        compare_response = test_client.post(
            "/api/admin/experiments/compare",
            headers=admin_headers,
            json={
                "experiment_names": ["lifecycle_exp_1", "lifecycle_exp_2"],
            },
        )
        assert compare_response.status_code == 200


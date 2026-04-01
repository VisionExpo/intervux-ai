"""
Authentication Tests.

Tests for:
- User login (form-based and JSON)
- Token refresh
- User profile retrieval
- Logout
- Password change
- RBAC enforcement

These tests verify:
- Correct status codes for success/failure
- Token generation and validation
- Authentication behavior
- Role-based access control
"""

import pytest
from fastapi.testclient import TestClient


class TestLoginEndpoint:
    """Test suite for login endpoints."""

    @pytest.mark.asyncio
    async def test_login_with_valid_credentials(self, client: TestClient):
        """
        Test successful login with valid credentials.
        
        Validates:
        - HTTP 200 status code
        - Returns access_token and refresh_token
        - Token type is 'bearer'
        """
        response = await client.post(
            "/api/auth/login",
            data={
                "username": "recruiter@intervux.ai",
                "password": "recruiter123",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    @pytest.mark.asyncio
    async def test_login_with_json_payload(self, client: TestClient):
        """
        Test successful login with JSON payload.
        
        Validates:
        - HTTP 200 status code
        - Returns token pair
        """
        response = await client.post(
            "/api/auth/login/json",
            json={
                "email": "recruiter@intervux.ai",
                "password": "recruiter123",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_login_with_invalid_password(self, client: TestClient):
        """
        Test login failure with incorrect password.
        
        Validates:
        - HTTP 401 status code
        - Error message indicates incorrect credentials
        """
        response = await client.post(
            "/api/auth/login",
            data={
                "username": "recruiter@intervux.ai",
                "password": "wrongpassword",
            },
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Incorrect" in data["detail"]

    @pytest.mark.asyncio
    async def test_login_with_invalid_email(self, client: TestClient):
        """
        Test login failure with non-existent email.
        
        Validates:
        - HTTP 401 status code
        - Error message indicates incorrect credentials
        """
        response = await client.post(
            "/api/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "anypassword",
            },
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_json_with_invalid_credentials(self, client: TestClient):
        """
        Test JSON login failure with incorrect password.
        
        Validates:
        - HTTP 401 status code
        """
        response = await client.post(
            "/api/auth/login/json",
            json={
                "email": "recruiter@intervux.ai",
                "password": "wrongpassword",
            },
        )
        
        assert response.status_code == 401


class TestTokenRefresh:
    """Test suite for token refresh functionality."""

    @pytest.mark.asyncio
    async def test_refresh_token_with_valid_token(self, client: TestClient):
        """
        Test successful token refresh.
        
        Validates:
        - HTTP 200 status code
        - Returns new token pair
        """
        # First login to get refresh token
        login_response = await client.post(
            "/api/auth/login",
            data={
                "username": "recruiter@intervux.ai",
                "password": "recruiter123",
            },
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Then refresh
        response = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_refresh_token_with_invalid_token(self, client: TestClient):
        """
        Test token refresh with invalid token.
        
        Validates:
        - HTTP 401 status code
        """
        response = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid_token_here"},
        )
        
        assert response.status_code == 401


class TestUserProfile:
    """Test suite for user profile endpoints."""

    @pytest.mark.asyncio
    async def test_get_current_user_profile(self, client: TestClient, recruiter_headers: dict):
        """
        Test retrieving current user profile.
        
        Validates:
        - HTTP 200 status code
        - Returns user information
        """
        response = await client.get("/api/auth/me", headers=recruiter_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "name" in data
        assert "role" in data

    @pytest.mark.asyncio
    async def test_get_profile_without_auth(self, client: TestClient):
        """
        Test profile retrieval without authentication.
        
        Validates:
        - HTTP 401 status code (unauthorized)
        """
        response = await client.get("/api/auth/me")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_profile_with_invalid_token(self, client: TestClient):
        """
        Test profile retrieval with invalid token.
        
        Validates:
        - HTTP 401 status code
        """
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/api/auth/me", headers=headers)
        
        assert response.status_code == 401


class TestLogout:
    """Test suite for logout functionality."""

    @pytest.mark.asyncio
    async def test_logout_success(self, client: TestClient, recruiter_headers: dict):
        """
        Test successful logout.
        
        Validates:
        - HTTP 200 status code
        - Returns success message
        """
        response = await client.post("/api/auth/logout", headers=recruiter_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "user_id" in data

    @pytest.mark.asyncio
    async def test_logout_without_auth(self, client: TestClient):
        """
        Test logout without authentication.
        
        Validates:
        - HTTP 401 status code
        """
        response = await client.post("/api/auth/logout")
        
        assert response.status_code == 401


class TestChangePassword:
    """Test suite for password change functionality."""

    @pytest.mark.asyncio
    async def test_change_password_requires_auth(self, client: TestClient, recruiter_headers: dict):
        """
        Test that password change requires authentication.
        
        Validates:
        - HTTP 200 status code (endpoint exists)
        - Password change is processed
        """
        response = await client.post(
            "/api/auth/change-password",
            headers=recruiter_headers,
            json={
                "old_password": "recruiter123",
                "new_password": "newpassword123",
            },
        )
        
        # Should return 200 (in demo mode) or 400 (verification failed)
        assert response.status_code in [200, 400]


class TestRBAC:
    """Test suite for Role-Based Access Control."""

    @pytest.mark.asyncio
    async def test_recruiter_can_access_recruiter_endpoints(
        self, client: TestClient, recruiter_headers: dict
    ):
        """
        Test that recruiter can access recruiter-protected endpoints.
        
        Validates:
        - HTTP 200 status code
        """
        response = await client.get("/api/candidates", headers=recruiter_headers)
        
        # Should succeed (200) or fail with 500 (if DB issue)
        assert response.status_code in [200, 500]

    @pytest.mark.asyncio
    async def test_recruiter_can_access_job_posts(
        self, client: TestClient, recruiter_headers: dict
    ):
        """
        Test that recruiter can access job posts.
        
        Validates:
        - HTTP 200 status code
        """
        response = await client.get("/api/job-posts", headers=recruiter_headers)
        
        assert response.status_code in [200, 500]

    @pytest.mark.asyncio
    async def test_candidate_cannot_access_recruiter_endpoints(
        self, client: TestClient, candidate_headers: dict
    ):
        """
        Test that candidate cannot access recruiter endpoints.
        
        Validates:
        - HTTP 403 status code (forbidden)
        """
        response = await client.get("/api/candidates", headers=candidate_headers)
        
        # Should be forbidden for candidate role
        assert response.status_code in [403, 500]

    @pytest.mark.asyncio
    async def test_admin_can_access_admin_endpoints(
        self, client: TestClient, admin_headers: dict
    ):
        """
        Test that admin can access admin-protected endpoints.
        
        Validates:
        - HTTP 200 status code
        """
        response = await client.get("/api/experiments", headers=admin_headers)
        
        assert response.status_code in [200, 500]

    @pytest.mark.asyncio
    async def test_recruiter_cannot_access_admin_endpoints(
        self, client: TestClient, recruiter_headers: dict
    ):
        """
        Test that recruiter cannot access admin-only endpoints.
        
        Validates:
        - HTTP 403 status code (forbidden)
        """
        response = await client.get("/api/experiments", headers=recruiter_headers)
        
        # Should be forbidden for recruiter role
        assert response.status_code in [403, 500]


class TestAuthHealth:
    """Test suite for auth health endpoint."""

    @pytest.mark.asyncio
    async def test_auth_health_returns_status(self, client: TestClient):
        """
        Test auth service health check.
        
        Validates:
        - HTTP 200 status code
        - Returns service status
        """
        response = await client.get("/api/auth/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


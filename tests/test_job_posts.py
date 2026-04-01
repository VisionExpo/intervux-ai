"""
Job Post Tests.

Tests for:
- Create job post
- List job posts
- Get single job post
- Update job post
- Delete job post

These tests verify:
- Correct status codes
- Response schemas
- Authentication behavior
- CRUD operations
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models.recruiter_dashboard_models import JobPostStatus


class TestCreateJobPost:
    """Test suite for creating job posts."""

    @pytest.mark.asyncio
async def test_create_job_post_success(
        self, client: TestClient, recruiter_headers: dict
    ):
        """
        Test successful job post creation.
        
        Validates:
        - HTTP 200 status code
        - Response contains created job post data
        - Job post has correct title and status
        """
        response = await client.post(
            "/api/job-posts",
            headers=recruiter_headers,
            json={
                "title": "Senior Software Engineer",
                "description": "We are hiring a senior software engineer",
                "experience_level": "senior",
                "ai_interview_enabled": True,
                "interview_limit": 10,
                "skills": ["Python", "FastAPI", "SQL"],
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["title"] == "Senior Software Engineer"
        assert data["experience_level"] == "senior"
        assert data["ai_interview_enabled"] is True

    @pytest.mark.asyncio
async def test_create_job_post_with_minimal_data(
        self, client: TestClient, recruiter_headers: dict
    ):
        """
        Test job post creation with minimal required data.
        
        Validates:
        - HTTP 200 status code
        - Default values are applied
        """
        response = await client.post(
            "/api/job-posts",
            headers=recruiter_headers,
            json={
                "title": "Junior Developer",
                "experience_level": "entry",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["title"] == "Junior Developer"
        assert data["status"] == JobPostStatus.DRAFT.value

    @pytest.mark.asyncio
async def test_create_job_post_without_auth(self, client: TestClient):
        """
        Test job post creation without authentication.
        
        Validates:
        - HTTP 401 status code (unauthorized)
        """
        response = await client.post(
            "/api/job-posts",
            json={
                "title": "Test Job",
                "experience_level": "mid",
            },
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
async def test_create_job_post_with_candidate_token(
        self, client: TestClient, candidate_headers: dict
    ):
        """
        Test job post creation with candidate token.
        
        Validates:
        - HTTP 403 status code (forbidden)
        """
        response = await client.post(
            "/api/job-posts",
            headers=candidate_headers,
            json={
                "title": "Test Job",
                "experience_level": "mid",
            },
        )
        
        assert response.status_code == 403


class TestListJobPosts:
    """Test suite for listing job posts."""

    @pytest.mark.asyncio
async def test_list_job_posts_success(
        self, client: TestClient, recruiter_headers: dict
    ):
        """
        Test successful job posts listing.
        
        Validates:
        - HTTP 200 status code
        - Response is a list
        """
        response = await client.get("/api/job-posts", headers=recruiter_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
async def test_list_job_posts_with_pagination(
        self, client: TestClient, recruiter_headers: dict
    ):
        """
        Test job posts listing with pagination.
        
        Validates:
        - Pagination parameters are accepted
        """
        response = await client.get(
            "/api/job-posts?page=1&limit=10",
            headers=recruiter_headers,
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
async def test_list_job_posts_with_status_filter(
        self, client: TestClient, recruiter_headers: dict
    ):
        """
        Test job posts listing with status filter.
        
        Validates:
        - Status filter parameter is accepted
        """
        response = await client.get(
            "/api/job-posts?status=active",
            headers=recruiter_headers,
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
async def test_list_job_posts_without_auth(self, client: TestClient):
        """
        Test job posts listing without authentication.
        
        Validates:
        - HTTP 401 status code
        """
        response = await client.get("/api/job-posts")
        
        assert response.status_code == 401


class TestGetJobPost:
    """Test suite for getting a single job post."""

    @pytest.mark.asyncio
async def test_get_job_post_success(
        self, 
        client: TestClient, 
        recruiter_headers: dict,
        test_job_post
    ):
        """
        Test successful job post retrieval.
        
        Validates:
        - HTTP 200 status code
        - Response contains job post details
        """
        response = await client.get(
            f"/api/job-posts/{test_job_post.id}",
            headers=recruiter_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_job_post.id
        assert "title" in data

    @pytest.mark.asyncio
async def test_get_job_post_not_found(
        self, client: TestClient, recruiter_headers: dict
    ):
        """
        Test job post retrieval with non-existent ID.
        
        Validates:
        - HTTP 404 status code
        """
        response = await client.get(
            "/api/job-posts/nonexistent-id",
            headers=recruiter_headers,
        )
        
        assert response.status_code == 404


class TestUpdateJobPost:
    """Test suite for updating job posts."""

    @pytest.mark.asyncio
async def test_update_job_post_success(
        self, 
        client: TestClient, 
        recruiter_headers: dict,
        test_job_post
    ):
        """
        Test successful job post update.
        
        Validates:
        - HTTP 200 status code
        - Job post is updated with new values
        """
        response = await client.put(
            f"/api/job-posts/{test_job_post.id}",
            headers=recruiter_headers,
            json={
                "title": "Updated Job Title",
                "status": "active",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Job Title"
        assert data["status"] == "active"

    @pytest.mark.asyncio
async def test_update_job_post_partial(
        self, 
        client: TestClient, 
        recruiter_headers: dict,
        test_job_post
    ):
        """
        Test partial job post update.
        
        Validates:
        - HTTP 200 status code
        - Only specified fields are updated
        """
        original_title = test_job_post.title
        
        response = await client.put(
            f"/api/job-posts/{test_job_post.id}",
            headers=recruiter_headers,
            json={
                "status": "closed",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        # Title should remain unchanged
        assert data["title"] == original_title
        assert data["status"] == "closed"

    @pytest.mark.asyncio
async def test_update_job_post_not_found(
        self, client: TestClient, recruiter_headers: dict
    ):
        """
        Test update of non-existent job post.
        
        Validates:
        - HTTP 404 status code
        """
        response = await client.put(
            "/api/job-posts/nonexistent-id",
            headers=recruiter_headers,
            json={
                "title": "Updated Title",
            },
        )
        
        assert response.status_code == 404


class TestDeleteJobPost:
    """Test suite for deleting job posts."""

    @pytest.mark.asyncio
async def test_delete_job_post_success(
        self, 
        client: TestClient, 
        recruiter_headers: dict,
        test_job_post
    ):
        """
        Test successful job post deletion.
        
        Validates:
        - HTTP 200 status code
        - Deletion confirmation message
        """
        response = await client.delete(
            f"/api/job-posts/{test_job_post.id}",
            headers=recruiter_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    @pytest.mark.asyncio
async def test_delete_job_post_not_found(
        self, client: TestClient, recruiter_headers: dict
    ):
        """
        Test deletion of non-existent job post.
        
        Validates:
        - HTTP 404 status code
        """
        response = await client.delete(
            "/api/job-posts/nonexistent-id",
            headers=recruiter_headers,
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
async def test_delete_job_post_without_auth(self, client: TestClient, test_job_post):
        """
        Test job post deletion without authentication.
        
        Validates:
        - HTTP 401 status code
        """
        response = await client.delete(f"/api/job-posts/{test_job_post.id}")
        
        assert response.status_code == 401


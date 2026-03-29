"""
Test Configuration and Fixtures for Intervux AI.

This module provides:
- Test database session with SQLite for isolation
- FastAPI TestClient
- Authentication fixtures for different user roles
- Test data factories

Usage:
    import pytest
    from tests.conftest import *
    
    def test_something(client, recruiter_token):
        headers = {"Authorization": f"Bearer {recruiter_token}"}
        response = client.get("/api/candidates", headers=headers)
        assert response.status_code == 200
"""

import os
import sys
import uuid
from datetime import datetime, timedelta
from typing import Any, Generator, Optional

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Set test environment variables before imports
os.environ["DATABASE_URL"] = "sqlite:///./tests/data/test_intervux.db"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["RUNTIME_THREADPOOL_WORKERS"] = "2"

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.database import Base, get_db
from backend.main import app
from backend.auth.jwt_service import (
    create_token_pair,
    hash_password,
    Role,
    DEMO_USERS,
)
from backend.models.recruiter_dashboard_models import (
    Candidate,
    CandidateStatus,
    ExperienceLevel,
    Interview,
    JobPost,
    JobPostStatus,
    JobSkill,
)


# =========================================================
# Test Database Engine
# =========================================================

TEST_DATABASE_URL = "sqlite:///./tests/data/test_intervux.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


# =========================================================
# Fixtures
# =========================================================


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Create a fresh database session for each test.
    
    Yields:
        SQLAlchemy session for database operations
    """
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    session = TestSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Create a FastAPI TestClient with test database.
    
    Yields:
        TestClient for making HTTP requests
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token() -> str:
    """
    Generate a valid JWT token for admin user.
    
    Returns:
        JWT access token string
    """
    user_data = {
        "user_id": "test-admin-001",
        "email": "admin@intervux.ai",
        "name": "Admin Test User",
        "role": Role.ADMIN,
    }
    token = create_token_pair(user_data)
    return token.access_token


@pytest.fixture
def recruiter_token() -> str:
    """
    Generate a valid JWT token for recruiter user.
    
    Returns:
        JWT access token string
    """
    user_data = {
        "user_id": "test-recruiter-001",
        "email": "recruiter@intervux.ai",
        "name": "Recruiter Test User",
        "role": Role.RECRUITER,
    }
    token = create_token_pair(user_data)
    return token.access_token


@pytest.fixture
def candidate_token() -> str:
    """
    Generate a valid JWT token for candidate user.
    
    Returns:
        JWT access token string
    """
    user_data = {
        "user_id": "test-candidate-001",
        "email": "candidate@intervux.ai",
        "name": "Candidate Test User",
        "role": Role.CANDIDATE,
    }
    token = create_token_pair(user_data)
    return token.access_token


@pytest.fixture
def admin_headers(admin_token: str) -> dict[str, str]:
    """
    Headers with admin authentication.
    
    Returns:
        Dictionary with Authorization header
    """
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def recruiter_headers(recruiter_token: str) -> dict[str, str]:
    """
    Headers with recruiter authentication.
    
    Returns:
        Dictionary with Authorization header
    """
    return {"Authorization": f"Bearer {recruiter_token}"}


@pytest.fixture
def candidate_headers(candidate_token: str) -> dict[str, str]:
    """
    Headers with candidate authentication.
    
    Returns:
        Dictionary with Authorization header
    """
    return {"Authorization": f"Bearer {candidate_token}"}


@pytest.fixture
def test_job_post(db_session: Session) -> JobPost:
    """
    Create a test job post in the database.
    
    Returns:
        JobPost model instance
    """
    job = JobPost(
        id=str(uuid.uuid4()),
        title="Senior Python Engineer",
        description="We are looking for a senior Python engineer",
        experience_level=ExperienceLevel.SENIOR.value,
        status=JobPostStatus.ACTIVE.value,
        ai_interview_enabled="true",
        interview_limit=10,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by="test-recruiter-001",
    )
    db_session.add(job)
    
    # Add skills
    skill = JobSkill(
        id=str(uuid.uuid4()),
        job_post_id=job.id,
        skill_name="Python",
        is_required="true",
    )
    db_session.add(skill)
    
    db_session.commit()
    db_session.refresh(job)
    return job


@pytest.fixture
def test_candidate(db_session: Session, test_job_post: JobPost) -> Candidate:
    """
    Create a test candidate in the database.
    
    Returns:
        Candidate model instance
    """
    candidate = Candidate(
        id=str(uuid.uuid4()),
        name="John Doe",
        email=f"john.doe.{uuid.uuid4().hex[:8]}@example.com",
        role="Python Engineer",
        resume_url="https://example.com/resume.pdf",
        status=CandidateStatus.INVITED.value,
        job_post_id=test_job_post.id,
        created_at=datetime.utcnow(),
    )
    db_session.add(candidate)
    db_session.commit()
    db_session.refresh(candidate)
    return candidate


@pytest.fixture
def test_interview(
    db_session: Session, 
    test_candidate: Candidate
) -> Interview:
    """
    Create a test interview in the database.
    
    Returns:
        Interview model instance
    """
    interview = Interview(
        id=str(uuid.uuid4()),
        candidate_id=test_candidate.id,
        role=test_candidate.role,
        overall_score=85.5,
        technical_score=90.0,
        communication_score=80.0,
        problem_solving_score=86.5,
        started_at=datetime.utcnow() - timedelta(minutes=30),
        completed_at=datetime.utcnow(),
    )
    db_session.add(interview)
    db_session.commit()
    db_session.refresh(interview)
    return interview


# =========================================================
# Helper Functions for Tests
# =========================================================


def create_test_job_post(
    db: Session,
    title: str = "Test Job Post",
    status: str = JobPostStatus.ACTIVE.value,
    experience_level: str = ExperienceLevel.MID.value,
) -> JobPost:
    """
    Helper to create a job post for testing.
    
    Args:
        db: Database session
        title: Job title
        status: Job status
        experience_level: Experience level
        
    Returns:
        Created JobPost instance
    """
    job = JobPost(
        id=str(uuid.uuid4()),
        title=title,
        description="Test job description",
        experience_level=experience_level,
        status=status,
        ai_interview_enabled="true",
        interview_limit=5,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by="test-recruiter-001",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def create_test_candidate(
    db: Session,
    name: str = "Test Candidate",
    email: Optional[str] = None,
    role: str = "Software Engineer",
    job_post_id: Optional[str] = None,
) -> Candidate:
    """
    Helper to create a candidate for testing.
    
    Args:
        db: Database session
        name: Candidate name
        email: Candidate email (auto-generated if not provided)
        role: Target role
        job_post_id: Associated job post ID
        
    Returns:
        Created Candidate instance
    """
    if email is None:
        email = f"{uuid.uuid4().hex[:8]}@test.com"
    
    candidate = Candidate(
        id=str(uuid.uuid4()),
        name=name,
        email=email,
        role=role,
        resume_url="https://example.com/resume.pdf",
        status=CandidateStatus.INVITED.value,
        job_post_id=job_post_id,
        created_at=datetime.utcnow(),
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


def create_test_interview(
    db: Session,
    candidate_id: str,
    role: str = "Software Engineer",
    overall_score: float = 75.0,
    technical_score: float = 80.0,
    communication_score: float = 70.0,
    problem_solving_score: float = 75.0,
) -> Interview:
    """
    Helper to create an interview for testing.
    
    Args:
        db: Database session
        candidate_id: Associated candidate ID
        role: Interview role
        overall_score: Overall score
        technical_score: Technical score
        communication_score: Communication score
        problem_solving_score: Problem solving score
        
    Returns:
        Created Interview instance
    """
    interview = Interview(
        id=str(uuid.uuid4()),
        candidate_id=candidate_id,
        role=role,
        overall_score=overall_score,
        technical_score=technical_score,
        communication_score=communication_score,
        problem_solving_score=problem_solving_score,
        started_at=datetime.utcnow() - timedelta(minutes=30),
        completed_at=datetime.utcnow(),
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


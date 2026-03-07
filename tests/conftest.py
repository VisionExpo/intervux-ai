import os
import sys
from pathlib import Path

import pytest
import httpx
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Ensure repo root is importable when pytest runs from different working dirs.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.db.database import SessionLocal
from backend.main import app
from backend.models.recruiter_dashboard_models import Interview
from backend.scripts.seed_dashboard import seed_dashboard


@pytest.fixture(scope="session", autouse=True)
def test_env():
    # Keep startup lightweight and deterministic in tests.
    os.environ.setdefault("TELEMETRY_DB_ENABLED", "false")
    os.environ.setdefault("TELEMETRY_JSONL_ENABLED", "false")


@pytest.fixture(scope="session")
def client():
    try:
        with TestClient(app) as test_client:
            yield test_client
            return
    except TypeError:
        pass

    # Fallback for httpx/starlette version mismatch in some environments.
    transport = httpx.ASGITransport(app=app)
    with httpx.Client(transport=transport, base_url="http://testserver") as test_client:
        yield test_client


@pytest.fixture(scope="session")
def admin_token(client):
    response = client.post(
        "/api/auth/login/json",
        json={"email": "admin@intervux.ai", "password": "admin123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="session")
def recruiter_token(client):
    response = client.post(
        "/api/auth/login/json",
        json={"email": "recruiter@intervux.ai", "password": "recruiter123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="session")
def recruiter_headers(recruiter_token):
    return {"Authorization": f"Bearer {recruiter_token}"}


@pytest.fixture(scope="session")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="session")
def sample_interview_id() -> str:
    db: Session = SessionLocal()
    try:
        row = db.query(Interview.id).first()
        if row:
            return row[0]
    finally:
        db.close()

    seed_dashboard()

    db = SessionLocal()
    try:
        row = db.query(Interview.id).first()
        assert row is not None
        return row[0]
    finally:
        db.close()

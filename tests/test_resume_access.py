import pytest
from fastapi.testclient import TestClient

from backend.core.security.jwt_service import Role, TokenData, get_current_user
from backend.main import app
from backend.modules.candidate.routes import resume_routes


@pytest.fixture
def resume_client():
    app.dependency_overrides.clear()
    yield TestClient(app, raise_server_exceptions=True)
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_resume_upload_requires_authentication(resume_client):
    response = resume_client.post(
        "/api/resume/upload",
        files={"file": ("resume.pdf", b"not parsed without authentication", "application/pdf")},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_resume_file_requires_authentication(resume_client, tmp_path, monkeypatch):
    monkeypatch.setattr(resume_routes, "RESUME_ROOT", tmp_path)
    owner_dir = tmp_path / "test-candidate-001"
    owner_dir.mkdir()
    (owner_dir / "resume.pdf").write_bytes(b"private resume")

    response = resume_client.get("/api/resume/files/test-candidate-001/resume.pdf")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_candidate_can_only_download_own_resume(resume_client, tmp_path, monkeypatch):
    monkeypatch.setattr(resume_routes, "RESUME_ROOT", tmp_path)
    owner_dir = tmp_path / "test-candidate-001"
    owner_dir.mkdir()
    (owner_dir / "resume.pdf").write_bytes(b"private resume")

    app.dependency_overrides[get_current_user] = lambda: TokenData(
        user_id="test-candidate-001", email="candidate@example.test", role=Role.CANDIDATE
    )
    own_response = resume_client.get(
        "/api/resume/files/test-candidate-001/resume.pdf",
    )
    other_response = resume_client.get(
        "/api/resume/files/another-candidate/resume.pdf",
    )

    assert own_response.status_code == 200
    assert own_response.content == b"private resume"
    assert other_response.status_code == 404


@pytest.mark.asyncio
async def test_old_public_upload_path_is_not_mounted(resume_client):
    response = resume_client.get("/uploads/resumes/test-candidate-001/resume.pdf")

    assert response.status_code == 404

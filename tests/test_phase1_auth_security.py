"""
Phase 1 security regressions (audit 2026-11-22).

S1  refresh tokens must not work as access tokens
S2  demo accounts are opt-in, never on in production, no built-in passwords
S3  recruiters cannot read or change another recruiter's jobs/candidates
S4  logout revokes only the presented token (no permanent lockout)
S5  diagnostics timeline is admin-only
S14 /api/auth/users is admin-only; change-password really changes the password
"""

import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect as sa_inspect

import backend.core.security.jwt_service as jwt_service
from backend.core.security.jwt_service import Role, create_token_pair
from backend.models.recruiter_dashboard_models import (
    Candidate,
    CandidateStatus,
    ExperienceLevel,
    JobPost,
    JobPostStatus,
)

OTHER_RECRUITER = "another-recruiter-999"


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# =========================================================
# S1 - token type
# =========================================================


class TestTokenType:
    @pytest.mark.asyncio
    async def test_refresh_token_rejected_on_protected_endpoint(self, client: TestClient):
        pair = create_token_pair(
            {"user_id": "test-recruiter-001", "email": "recruiter@intervux.ai",
             "name": "R", "role": Role.RECRUITER}
        )
        response = await client.get("/api/auth/me", headers=_bearer(pair.refresh_token))
        assert response.status_code == 401

        response = await client.get("/api/job-posts", headers=_bearer(pair.refresh_token))
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_access_token_rejected_as_refresh_token(self, client: TestClient):
        pair = create_token_pair(
            {"user_id": "test-recruiter-001", "email": "recruiter@intervux.ai",
             "name": "R", "role": Role.RECRUITER}
        )
        response = await client.post("/api/auth/refresh", json={"refresh_token": pair.access_token})
        assert response.status_code == 401
        # No internal exception text leaks to the client.
        assert response.json()["detail"] in {"Could not validate credentials", "Invalid refresh token"}

    @pytest.mark.asyncio
    async def test_refresh_token_issues_working_access_token(self, client: TestClient):
        pair = create_token_pair(
            {"user_id": "recruiter-001", "email": "recruiter@intervux.ai",
             "name": "R", "role": Role.RECRUITER}
        )
        response = await client.post("/api/auth/refresh", json={"refresh_token": pair.refresh_token})
        assert response.status_code == 200
        new_access = response.json()["access_token"]
        me = await client.get("/api/auth/me", headers=_bearer(new_access))
        assert me.status_code == 200

    def test_every_token_has_a_distinct_jti(self):
        pair = create_token_pair(
            {"user_id": "u1", "email": "u1@example.com", "role": Role.CANDIDATE}
        )
        access = jwt_service.decode_token(pair.access_token)
        refresh = jwt_service.decode_token(pair.refresh_token)
        assert access["jti"] and refresh["jti"]
        assert access["jti"] != refresh["jti"]
        assert access["type"] == "access" and refresh["type"] == "refresh"


# =========================================================
# S2 - demo accounts
# =========================================================


class TestDemoAccounts:
    def test_disabled_without_opt_in(self, monkeypatch):
        monkeypatch.delenv("ENABLE_DEMO_USERS", raising=False)
        assert jwt_service.build_demo_users() == {}

    def test_never_enabled_in_production(self, monkeypatch):
        monkeypatch.setenv("ENABLE_DEMO_USERS", "true")
        monkeypatch.setenv("ENV", "production")
        assert jwt_service.build_demo_users() == {}

    def test_no_default_passwords(self, monkeypatch):
        monkeypatch.setenv("ENABLE_DEMO_USERS", "true")
        monkeypatch.delenv("DEMO_ADMIN_PASS", raising=False)
        monkeypatch.delenv("DEMO_RECRUITER_PASS", raising=False)
        assert jwt_service.build_demo_users() == {}

    @pytest.mark.asyncio
    async def test_old_default_password_fails_when_demo_disabled(self, client: TestClient, monkeypatch):
        monkeypatch.setattr(jwt_service, "DEMO_USERS", {})
        response = await client.post(
            "/api/auth/login",
            data={"username": "admin@intervux.ai", "password": "admin123"},
        )
        assert response.status_code == 401


# =========================================================
# S4 - logout
# =========================================================


class TestLogout:
    @pytest.mark.asyncio
    async def test_logout_revokes_only_that_token(self, client: TestClient):
        first = await client.post(
            "/api/auth/login",
            data={"username": "recruiter@intervux.ai", "password": "recruiter123"},
        )
        assert first.status_code == 200
        first_token = first.json()["access_token"]

        out = await client.post("/api/auth/logout", headers=_bearer(first_token))
        assert out.status_code == 200

        # The logged-out token is dead...
        assert (await client.get("/api/auth/me", headers=_bearer(first_token))).status_code == 401

        # ...but the user can log in again and use the new token.
        second = await client.post(
            "/api/auth/login",
            data={"username": "recruiter@intervux.ai", "password": "recruiter123"},
        )
        assert second.status_code == 200
        second_token = second.json()["access_token"]
        assert (await client.get("/api/auth/me", headers=_bearer(second_token))).status_code == 200


# =========================================================
# S5 / S14 - admin-only endpoints
# =========================================================


class TestAdminOnlyEndpoints:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("headers_fixture", ["candidate_headers", "recruiter_headers"])
    async def test_diagnostics_timeline_forbidden_for_non_admin(
        self, client: TestClient, request, headers_fixture
    ):
        headers = request.getfixturevalue(headers_fixture)
        response = await client.get("/api/diagnostics/session/any-session/timeline", headers=headers)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_diagnostics_timeline_allowed_for_admin(self, client: TestClient, admin_headers):
        response = await client.get("/api/diagnostics/session/does-not-exist/timeline", headers=admin_headers)
        # Admin passes authorization; the session simply has no telemetry.
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_user_list_admin_only(self, client: TestClient, recruiter_headers, admin_headers):
        assert (await client.get("/api/auth/users", headers=recruiter_headers)).status_code == 403
        assert (await client.get("/api/auth/users", headers=admin_headers)).status_code == 200


class TestChangePassword:
    @pytest.mark.asyncio
    async def test_change_password_updates_database_user(self, client: TestClient):
        email = f"pw-{uuid.uuid4().hex[:8]}@example.com"
        signup = await client.post(
            "/api/candidate/signup",
            json={"name": "Pw User", "email": email, "password": "old-password-1"},
        )
        assert signup.status_code in (200, 201), signup.text
        token = signup.json()["access_token"]

        bad = await client.post(
            "/api/auth/change-password",
            headers=_bearer(token),
            json={"old_password": "wrong-password", "new_password": "new-password-1"},
        )
        assert bad.status_code == 400

        ok = await client.post(
            "/api/auth/change-password",
            headers=_bearer(token),
            json={"old_password": "old-password-1", "new_password": "new-password-1"},
        )
        assert ok.status_code == 200

        old_login = await client.post("/api/auth/login", data={"username": email, "password": "old-password-1"})
        new_login = await client.post("/api/auth/login", data={"username": email, "password": "new-password-1"})
        assert old_login.status_code == 401
        assert new_login.status_code == 200


# =========================================================
# S3 - recruiter data isolation
# =========================================================


@pytest.fixture
async def other_recruiter_job(db_session) -> JobPost:
    job = JobPost(
        id=f"other-job-{uuid.uuid4().hex[:8]}",
        title="Other recruiter's role",
        description="Not yours",
        experience_level=ExperienceLevel.MID.value,
        status=JobPostStatus.ACTIVE.value,
        ai_interview_enabled="true",
        interview_limit=5,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        recruiter_id=OTHER_RECRUITER,
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)
    return job


@pytest.fixture
async def other_recruiter_candidate(db_session, other_recruiter_job) -> Candidate:
    candidate = Candidate(
        id=f"other-cand-{uuid.uuid4().hex[:8]}",
        name="Other Candidate",
        email=f"other-{uuid.uuid4().hex[:8]}@example.com",
        role="Engineer",
        resume_url="",
        status=CandidateStatus.INVITED.value,
        job_post_id=other_recruiter_job.id,
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(candidate)
    await db_session.commit()
    await db_session.refresh(candidate)
    return candidate


class TestRecruiterIsolation:
    @pytest.mark.asyncio
    async def test_list_excludes_other_recruiters_jobs(
        self, client: TestClient, recruiter_headers, test_job_post, other_recruiter_job
    ):
        response = await client.get("/api/job-posts", headers=recruiter_headers)
        assert response.status_code == 200
        ids = {job["id"] for job in response.json()}
        assert test_job_post.id in ids
        assert other_recruiter_job.id not in ids

    @pytest.mark.asyncio
    async def test_admin_sees_all_jobs(
        self, client: TestClient, admin_headers, test_job_post, other_recruiter_job
    ):
        response = await client.get("/api/job-posts", headers=admin_headers)
        ids = {job["id"] for job in response.json()}
        assert {test_job_post.id, other_recruiter_job.id} <= ids

    @pytest.mark.asyncio
    async def test_cannot_get_update_or_delete_other_recruiters_job(
        self, client: TestClient, recruiter_headers, other_recruiter_job
    ):
        url = f"/api/job-posts/{other_recruiter_job.id}"
        assert (await client.get(url, headers=recruiter_headers)).status_code == 404
        assert (await client.put(url, headers=recruiter_headers, json={"title": "pwned"})).status_code == 404
        assert (await client.delete(url, headers=recruiter_headers)).status_code == 404

    @pytest.mark.asyncio
    async def test_owner_and_admin_can_get_job(
        self, client: TestClient, recruiter_headers, admin_headers, test_job_post, other_recruiter_job
    ):
        # Read primary keys from the identity map: fixture/app commits on the
        # shared session expire ORM objects, and a lazy reload needs async IO.
        own_id = sa_inspect(test_job_post).identity[0]
        other_id = sa_inspect(other_recruiter_job).identity[0]
        assert (await client.get(f"/api/job-posts/{own_id}", headers=recruiter_headers)).status_code == 200
        assert (await client.get(f"/api/job-posts/{other_id}", headers=admin_headers)).status_code == 200

    @pytest.mark.asyncio
    async def test_cannot_invite_into_other_recruiters_job(
        self, client: TestClient, recruiter_headers, other_recruiter_job
    ):
        response = await client.post(
            "/api/candidates/invite",
            headers=recruiter_headers,
            json={
                "name": "Sneaky",
                "email": "sneaky@example.com",
                "role": "Engineer",
                "job_post_id": other_recruiter_job.id,
            },
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_cannot_touch_other_recruiters_candidate(
        self, client: TestClient, recruiter_headers, other_recruiter_candidate
    ):
        cid = other_recruiter_candidate.id
        link = await client.post(f"/api/candidates/{cid}/generate-link", headers=recruiter_headers)
        assert link.status_code == 404
        status_resp = await client.patch(
            f"/api/candidates/{cid}/status", headers=recruiter_headers, params={"status": "completed"}
        )
        assert status_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_candidate_status_must_be_valid(
        self, client: TestClient, recruiter_headers, test_candidate
    ):
        response = await client.patch(
            f"/api/candidates/{test_candidate.id}/status",
            headers=recruiter_headers,
            params={"status": "hired-lol"},
        )
        assert response.status_code == 422

        ok = await client.patch(
            f"/api/candidates/{test_candidate.id}/status",
            headers=recruiter_headers,
            params={"status": CandidateStatus.COMPLETED.value},
        )
        assert ok.status_code == 200

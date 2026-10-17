from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.core.security.rbac import can_access_interview
from backend.models.recruiter_dashboard_models import Candidate, JobPost
from backend.services.recruiter_dashboard_store import ensure_interview_access, list_candidates


def test_interview_access_policy_requires_matching_owner_for_non_admins():
    assert can_access_interview("admin", "assigned-recruiter", "other-user")
    assert can_access_interview("recruiter", "assigned-recruiter", "assigned-recruiter")
    assert not can_access_interview("recruiter", "assigned-recruiter", "other-recruiter")
    assert not can_access_interview("viewer", "assigned-recruiter", "unassigned-viewer")
    assert not can_access_interview("viewer", "", "unassigned-viewer")
    assert not can_access_interview("unknown", "assigned-recruiter", "assigned-recruiter")


@pytest.mark.asyncio
async def test_assigned_recruiter_can_access_interview(db_session, test_interview):
    user = SimpleNamespace(role="recruiter", user_id="test-recruiter-001")

    await ensure_interview_access(db_session, test_interview.id, user)


@pytest.mark.asyncio
async def test_unassigned_recruiter_cannot_access_interview(db_session, test_interview):
    user = SimpleNamespace(role="recruiter", user_id="another-recruiter")

    with pytest.raises(HTTPException) as error:
        await ensure_interview_access(db_session, test_interview.id, user)

    assert error.value.status_code == 404


@pytest.mark.asyncio
async def test_viewer_without_assignment_cannot_access_interview(db_session, test_interview):
    user = SimpleNamespace(role="viewer", user_id="unassigned-viewer")

    with pytest.raises(HTTPException) as error:
        await ensure_interview_access(db_session, test_interview.id, user)

    assert error.value.status_code == 404


@pytest.mark.asyncio
async def test_candidate_list_is_scoped_to_recruiter_assignment(
    db_session, test_candidate
):
    other_job = JobPost(
        id="other-recruiter-job",
        recruiter_id="another-recruiter",
        title="Other recruiter role",
        experience_level="mid",
    )
    other_candidate = Candidate(
        id="other-recruiter-candidate",
        name="Other Candidate",
        email="other-candidate@example.test",
        role="Engineer",
        job_post_id=other_job.id,
    )
    db_session.add_all([other_job, other_candidate])
    await db_session.flush()

    assigned_rows = await list_candidates(db_session, recruiter_id="test-recruiter-001")
    unassigned_rows = await list_candidates(db_session, recruiter_id="unknown-recruiter")

    assert [row["id"] for row in assigned_rows] == [test_candidate.id]
    assert unassigned_rows == []

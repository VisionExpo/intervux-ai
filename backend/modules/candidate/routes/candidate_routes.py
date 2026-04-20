"""
Candidate Portal API Routes

This module provides API endpoints for:
- Candidate signup
- Candidate profile management
- Resume upload
- Mock interviews
- Notifications
"""

import asyncio
import json
import os
import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status

from backend.core.security.jwt_service import (
    Token,
    TokenData,
    Role,
    create_token_pair,
    get_current_user,
    hash_password,
)
from backend.infrastructure.database.database import AsyncSessionLocal
from sqlalchemy import select
from backend.models.candidate_portal import CandidateProfile, MockInterview, Notification
from backend.services.resume_parser_service import ParsedResume, parse_resume_from_upload
from backend.core.logging.logger import get_logger
from backend.modules.candidate.schemas import (
    CandidateSignup,
    CandidateProfileResponse,
    CandidateProfileUpdate,
    ResumeUploadResponse,
    MockInterviewResponse,
    MockInterviewStartResponse,
    NotificationResponse,
    DashboardResponse,
)
from backend.modules.candidate.services.profile_scoring import (
    RESUME_RATE_LIMIT_MAX_ATTEMPTS,
    RESUME_RATE_LIMIT_WINDOW_S,
    allow_resume_attempt,
    allow_signup_attempt,
    calculate_profile_score,
    calculate_resume_score,
)

router = APIRouter()
logger = get_logger(__name__)


# =========================================================
# Auth Routes
# =========================================================


@router.post("/signup", response_model=Token)
async def candidate_signup(candidate_data: CandidateSignup, request: Request):
    """Register a new candidate."""
    from backend.infrastructure.database.database import User

    client_ip = request.client.host if request.client and request.client.host else "unknown"
    if not allow_signup_attempt(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many signup attempts. Please try again later.",
        )

    async with AsyncSessionLocal() as db:
        res = await db.execute(select(User).filter(User.email == candidate_data.email))
        existing_user = res.scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        try:
            db_user = User(
                email=candidate_data.email,
                password_hash=hash_password(candidate_data.password),
                name=candidate_data.name,
                role=Role.CANDIDATE,
            )
            db.add(db_user)
            await db.flush()

            user_id = f"candidate-{db_user.id}"

            # Link invitation if token present
            if candidate_data.invite_token:
                from backend.models.recruiter_dashboard_models import Candidate as RecruiterCandidate
                link_pattern = f"%/invite/{candidate_data.invite_token}%"
                inv_res = await db.execute(select(RecruiterCandidate).filter(RecruiterCandidate.interview_link.like(link_pattern)))
                recruiter_candidate = inv_res.scalar_one_or_none()
                if recruiter_candidate:
                    recruiter_candidate.status = "scheduled" # Mark as ready for interview
                    logger.info(f"Linked new user to invitation for {recruiter_candidate.name}")

            profile = CandidateProfile(
                user_id=user_id,
                name=candidate_data.name,
                skills="[]",
                mock_interviews_remaining=3,
            )
            db.add(profile)
            await db.commit()
        except Exception:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Signup failed, please try again")

        user_data = {
            "user_id": user_id,
            "email": candidate_data.email,
            "name": candidate_data.name,
            "role": Role.CANDIDATE,
        }
        return create_token_pair(user_data)


# =========================================================
# Profile Routes
# =========================================================


@router.get("/profile", response_model=CandidateProfileResponse)
async def get_candidate_profile(current_user: TokenData = Depends(get_current_user)):
    if current_user.role != Role.CANDIDATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only candidates can access this endpoint")

    async with AsyncSessionLocal() as db:
        res = await db.execute(select(CandidateProfile).filter(CandidateProfile.user_id == current_user.user_id))
        profile = res.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        skills = json.loads(profile.skills) if profile.skills else []

        return CandidateProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            name=profile.name,
            skills=skills,
            experience_years=profile.experience_years,
            education=profile.education,
            resume_url=profile.resume_url,
            resume_score=profile.resume_score,
            interview_score=profile.interview_score,
            profile_score=profile.profile_score or calculate_profile_score(profile),
            github_url=profile.github_url,
            linkedin_url=profile.linkedin_url,
            mock_interviews_remaining=profile.mock_interviews_remaining,
            created_at=profile.created_at,
        )


@router.put("/profile", response_model=CandidateProfileResponse)
async def update_candidate_profile(
    profile_update: CandidateProfileUpdate,
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.role != Role.CANDIDATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only candidates can access this endpoint")

    async with AsyncSessionLocal() as db:
        res = await db.execute(select(CandidateProfile).filter(CandidateProfile.user_id == current_user.user_id))
        profile = res.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        if profile_update.name is not None:
            profile.name = profile_update.name
        if profile_update.skills is not None:
            profile.skills = json.dumps(profile_update.skills)
        if profile_update.experience_years is not None:
            profile.experience_years = profile_update.experience_years
        if profile_update.education is not None:
            profile.education = profile_update.education
        if profile_update.github_url is not None:
            profile.github_url = profile_update.github_url
        if profile_update.linkedin_url is not None:
            profile.linkedin_url = profile_update.linkedin_url

        profile.profile_score = calculate_profile_score(profile)
        profile.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(profile)

        skills = json.loads(profile.skills) if profile.skills else []

        return CandidateProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            name=profile.name,
            skills=skills,
            experience_years=profile.experience_years,
            education=profile.education,
            resume_url=profile.resume_url,
            resume_score=profile.resume_score,
            interview_score=profile.interview_score,
            profile_score=profile.profile_score,
            github_url=profile.github_url,
            linkedin_url=profile.linkedin_url,
            mock_interviews_remaining=profile.mock_interviews_remaining,
            created_at=profile.created_at,
        )


# =========================================================
# Resume Routes
# =========================================================


@router.post("/resume", response_model=ResumeUploadResponse)
async def upload_resume(
    request: Request,
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Upload and parse a candidate resume.

    Uses the unified ResumeParserService (Gemini primary, text fallback)
    instead of calling agent_ocr directly.
    """
    if current_user.role != Role.CANDIDATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only candidates can access this endpoint")

    if not allow_resume_attempt(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many resume uploads. Maximum {RESUME_RATE_LIMIT_MAX_ATTEMPTS} per {RESUME_RATE_LIMIT_WINDOW_S}s.",
        )

    allowed_extensions = {".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg"}
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed: PDF, DOCX, DOC, PNG, JPG",
        )

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 10MB.",
        )

    async with AsyncSessionLocal() as db:
        res = await db.execute(select(CandidateProfile).filter(
            CandidateProfile.user_id == current_user.user_id
        ))
        profile = res.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        # Save file to disk
        upload_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "uploads", "resumes", current_user.user_id
        )
        os.makedirs(upload_dir, exist_ok=True)

        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = os.path.join(upload_dir, unique_filename)

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # Parse via unified service in threadpool to avoid blocking event loop.
        file.file.seek(0)
        try:
            parsed: ParsedResume = await asyncio.to_thread(parse_resume_from_upload, file)
        except Exception:
            logger.exception("Resume parsing failed in candidate upload")
            parsed = ParsedResume()

        resume_score, strengths, weaknesses = calculate_resume_score(parsed)

        resume_url = f"/uploads/resumes/{current_user.user_id}/{unique_filename}"

        profile.resume_url = resume_url
        profile.resume_score = resume_score
        profile.skills = json.dumps(parsed.skills)
        profile.profile_score = calculate_profile_score(profile)
        profile.updated_at = datetime.utcnow()

        await db.commit()

        notification = Notification(
            user_id=current_user.user_id,
            type="resume_analyzed",
            message=f"Your resume has been analyzed. Score: {resume_score:.0f}%",
        )
        db.add(notification)
        await db.commit()

        return ResumeUploadResponse(
            resume_url=resume_url,
            resume_score=resume_score,
            skills=parsed.skills,
            strengths=strengths,
            weaknesses=weaknesses,
        )


# =========================================================
# Mock Interview Routes
# =========================================================


@router.post("/mock-interview/start", response_model=MockInterviewStartResponse)
async def start_mock_interview(current_user: TokenData = Depends(get_current_user)):
    if current_user.role != Role.CANDIDATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only candidates can access this endpoint")

    from sqlalchemy import func
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(CandidateProfile).filter(
            CandidateProfile.user_id == current_user.user_id
        ))
        profile = res.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        if profile.mock_interviews_remaining <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No mock interviews remaining. Upgrade to get more.",
            )

        count_res = await db.execute(select(func.count(MockInterview.id)).filter(
            MockInterview.candidate_id == profile.id
        ))
        existing_count = count_res.scalar()

        session_id = f"mock-{uuid.uuid4().hex}"
        mock_interview = MockInterview(
            candidate_id=profile.id,
            session_id=session_id,
            status="in_progress",
            interview_number=existing_count + 1,
        )
        db.add(mock_interview)

# Credit deducted on completion

        await db.commit()
        await db.refresh(mock_interview)

        return MockInterviewStartResponse(
            session_id=session_id,
            message="Mock interview started. Connect to WebSocket for the interview.",
            mock_interview_id=mock_interview.id,
        )


@router.get("/mock-interview/history", response_model=List[MockInterviewResponse])
async def get_mock_interview_history(current_user: TokenData = Depends(get_current_user)):
    if current_user.role != Role.CANDIDATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only candidates can access this endpoint")

    async with AsyncSessionLocal() as db:
        res = await db.execute(select(CandidateProfile).filter(
            CandidateProfile.user_id == current_user.user_id
        ))
        profile = res.scalar_one_or_none()
        if not profile:
            return []

        i_res = await db.execute(select(MockInterview)
            .filter(MockInterview.candidate_id == profile.id)
            .order_by(MockInterview.created_at.desc()))
        interviews = i_res.scalars().all()

        return [
            MockInterviewResponse(
                id=i.id,
                session_id=i.session_id,
                score=i.score,
                technical_score=i.technical_score,
                communication_score=i.communication_score,
                reasoning_score=i.reasoning_score,
                status=i.status,
                interview_number=i.interview_number,
                created_at=i.created_at,
                completed_at=i.completed_at,
            )
            for i in interviews
        ]


@router.get("/mock-interview/{interview_id}", response_model=MockInterviewResponse)
async def get_mock_interview(
    interview_id: int,
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.role != Role.CANDIDATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only candidates can access this endpoint")

    async with AsyncSessionLocal() as db:
        res = await db.execute(select(CandidateProfile).filter(
            CandidateProfile.user_id == current_user.user_id
        ))
        profile = res.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        i_res = await db.execute(select(MockInterview).filter(
            MockInterview.id == interview_id,
            MockInterview.candidate_id == profile.id,
        ))
        interview = i_res.scalar_one_or_none()
        if not interview:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")

        return MockInterviewResponse(
            id=interview.id,
            session_id=interview.session_id,
            score=interview.score,
            technical_score=interview.technical_score,
            communication_score=interview.communication_score,
            reasoning_score=interview.reasoning_score,
            status=interview.status,
            interview_number=interview.interview_number,
            created_at=interview.created_at,
            completed_at=interview.completed_at,
        )


# =========================================================
# Notification Routes
# =========================================================


@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(current_user: TokenData = Depends(get_current_user)):
    if current_user.role != Role.CANDIDATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only candidates can access this endpoint")

    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Notification)
            .filter(Notification.user_id == current_user.user_id)
            .order_by(Notification.created_at.desc())
            .limit(50))
        notifications = res.scalars().all()

        return [
            NotificationResponse(
                id=n.id,
                type=n.type,
                message=n.message,
                is_read=n.is_read,
                created_at=n.created_at,
            )
            for n in notifications
        ]


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.role != Role.CANDIDATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only candidates can access this endpoint")

    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.user_id,
        ))
        notification = res.scalar_one_or_none()
        if not notification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

        notification.is_read = True
        await db.commit()

        return {"message": "Notification marked as read"}


# =========================================================
# Dashboard Route
# =========================================================


@router.get("/dashboard", response_model=DashboardResponse)
async def get_candidate_dashboard(current_user: TokenData = Depends(get_current_user)):
    if current_user.role != Role.CANDIDATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only candidates can access this endpoint")

    async with AsyncSessionLocal() as db:
        res = await db.execute(select(CandidateProfile).filter(
            CandidateProfile.user_id == current_user.user_id
        ))
        profile = res.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        recent_activity = []

        i_res = await db.execute(select(MockInterview)
            .filter(
                MockInterview.candidate_id == profile.id,
                MockInterview.status == "completed",
            )
            .order_by(MockInterview.completed_at.desc()))
        recent_interview = i_res.scalars().first()

        if recent_interview:
            if recent_interview.score is not None:
                recent_activity.append(f"Mock Interview #{recent_interview.interview_number} completed - Score: {recent_interview.score:.0f}")
            else:
                recent_activity.append(f"Mock Interview #{recent_interview.interview_number} completed")


        if profile.resume_url:
            recent_activity.append("Resume analyzed")

        if profile.profile_score and profile.profile_score >= 50:
            recent_activity.append("Profile updated")

        ci_res = await db.execute(select(MockInterview)
            .filter(
                MockInterview.candidate_id == profile.id,
                MockInterview.status == "completed",
                MockInterview.score.isnot(None),
            ))
        completed_interviews = ci_res.scalars().all()

        mock_interview_score = (
            sum(i.score for i in completed_interviews) / len(completed_interviews)
            if completed_interviews
            else 0.0
        )

        return DashboardResponse(
            profile_score=profile.profile_score or 0.0,
            resume_score=profile.resume_score or 0.0,
            mock_interview_score=mock_interview_score,
            mock_interviews_remaining=profile.mock_interviews_remaining,
            recent_activity=recent_activity,
        )

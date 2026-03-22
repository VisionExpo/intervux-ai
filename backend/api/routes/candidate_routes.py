"""
Candidate Portal API Routes

This module provides API endpoints for:
- Candidate signup
- Candidate profile management
- Resume upload
- Mock interviews
- Notifications
"""

import json
import os
import time
import uuid
from datetime import datetime
from threading import Lock
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from pydantic import BaseModel

from backend.auth.jwt_service import (
    Token,
    TokenData,
    Role,
    create_token_pair,
    get_current_user,
    hash_password,
)
from backend.db.database import SessionLocal
from backend.models.candidate_portal import CandidateProfile, MockInterview, Notification
from backend.services.resume_parser_service import ParsedResume, parse_resume_from_upload
from backend.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

SIGNUP_RATE_LIMIT_WINDOW_S = int(os.getenv("SIGNUP_RATE_LIMIT_WINDOW_S", "300"))
SIGNUP_RATE_LIMIT_MAX_ATTEMPTS = int(os.getenv("SIGNUP_RATE_LIMIT_MAX_ATTEMPTS", "10"))
_signup_hits: dict[str, list[float]] = {}
_signup_lock = Lock()


def _allow_signup_attempt(ip: str) -> bool:
    now = time.time()
    window_start = now - SIGNUP_RATE_LIMIT_WINDOW_S
    with _signup_lock:
        attempts = [ts for ts in _signup_hits.get(ip, []) if ts >= window_start]
        if len(attempts) >= SIGNUP_RATE_LIMIT_MAX_ATTEMPTS:
            _signup_hits[ip] = attempts
            return False
        attempts.append(now)
        _signup_hits[ip] = attempts
        return True


# =========================================================
# Pydantic Models
# =========================================================


class CandidateSignup(BaseModel):
    email: str
    password: str
    name: str


class CandidateProfileResponse(BaseModel):
    id: int
    user_id: str
    name: str
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    education: Optional[str] = None
    resume_url: Optional[str] = None
    resume_score: Optional[float] = None
    interview_score: Optional[float] = None
    profile_score: Optional[float] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    mock_interviews_remaining: int
    created_at: datetime


class CandidateProfileUpdate(BaseModel):
    name: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    education: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None


class ResumeUploadResponse(BaseModel):
    resume_url: str
    resume_score: float
    skills: List[str]
    strengths: List[str]
    weaknesses: List[str]


class MockInterviewResponse(BaseModel):
    id: int
    session_id: str
    score: Optional[float] = None
    technical_score: Optional[float] = None
    communication_score: Optional[float] = None
    reasoning_score: Optional[float] = None
    status: str
    interview_number: int
    created_at: datetime
    completed_at: Optional[datetime] = None


class MockInterviewStartResponse(BaseModel):
    session_id: str
    message: str
    mock_interview_id: int


class NotificationResponse(BaseModel):
    id: int
    type: str
    message: str
    is_read: bool
    created_at: datetime


class DashboardResponse(BaseModel):
    profile_score: float
    resume_score: float
    mock_interview_score: float
    mock_interviews_remaining: int
    recent_activity: List[str]


# =========================================================
# Helper Functions
# =========================================================


def _calculate_profile_score(profile: CandidateProfile) -> float:
    score = 0.0

    if profile.name:
        score += 20

    if profile.skills:
        skills = json.loads(profile.skills) if isinstance(profile.skills, str) else profile.skills
        score += min(len(skills) * 3, 30)

    if profile.experience_years:
        score += min(profile.experience_years * 2, 20)

    if profile.education:
        score += 15

    if profile.resume_url:
        score += 15

    return min(score, 100)


def _calculate_resume_score(
    parsed: ParsedResume,
) -> tuple[float, List[str], List[str]]:
    """
    Derive a 0-100 score plus strengths/weaknesses from a ParsedResume.

    Previously accepted a raw dict from agent_ocr; now accepts the
    canonical ParsedResume so both Gemini and text-parser results are
    handled identically.
    """
    score = 50.0
    strengths: List[str] = []
    weaknesses: List[str] = []

    if parsed.skills:
        score += min(len(parsed.skills) * 5, 25)
        strengths.append(f"{len(parsed.skills)} skills identified")

    if parsed.projects:
        score += min(len(parsed.projects) * 5, 15)
        strengths.append(f"{len(parsed.projects)} projects documented")

    if parsed.experience:
        score += 10
        strengths.append("Work experience present")
    else:
        weaknesses.append("No work experience mentioned")

    if parsed.education:
        score += 10
    else:
        weaknesses.append("Education details missing")

    return min(score, 100), strengths, weaknesses


# =========================================================
# Auth Routes
# =========================================================


@router.post("/signup", response_model=Token)
async def candidate_signup(candidate_data: CandidateSignup, request: Request):
    """Register a new candidate."""
    from backend.db.database import User

    client_ip = request.client.host if request.client and request.client.host else "unknown"
    if not _allow_signup_attempt(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many signup attempts. Please try again later.",
        )

    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == candidate_data.email).first()
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
            db.flush()

            user_id = f"candidate-{db_user.id}"

            profile = CandidateProfile(
                user_id=user_id,
                name=candidate_data.name,
                skills="[]",
                mock_interviews_remaining=3,
            )
            db.add(profile)
            db.commit()
        except Exception:
            db.rollback()
            raise HTTPException(status_code=500, detail="Signup failed, please try again")

        user_data = {
            "user_id": user_id,
            "email": candidate_data.email,
            "name": candidate_data.name,
            "role": Role.CANDIDATE,
        }
        return create_token_pair(user_data)

    finally:
        db.close()


# =========================================================
# Profile Routes
# =========================================================


@router.get("/profile", response_model=CandidateProfileResponse)
async def get_candidate_profile(current_user: TokenData = Depends(get_current_user)):
    if current_user.role != Role.CANDIDATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only candidates can access this endpoint")

    db = SessionLocal()
    try:
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.user_id).first()
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
            profile_score=profile.profile_score or _calculate_profile_score(profile),
            github_url=profile.github_url,
            linkedin_url=profile.linkedin_url,
            mock_interviews_remaining=profile.mock_interviews_remaining,
            created_at=profile.created_at,
        )
    finally:
        db.close()


@router.put("/profile", response_model=CandidateProfileResponse)
async def update_candidate_profile(
    profile_update: CandidateProfileUpdate,
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.role != Role.CANDIDATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only candidates can access this endpoint")

    db = SessionLocal()
    try:
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.user_id).first()
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

        profile.profile_score = _calculate_profile_score(profile)
        profile.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(profile)

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
    finally:
        db.close()


# =========================================================
# Resume Routes
# =========================================================


@router.post("/resume", response_model=ResumeUploadResponse)
async def upload_resume(
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

    db = SessionLocal()
    try:
        profile = db.query(CandidateProfile).filter(
            CandidateProfile.user_id == current_user.user_id
        ).first()
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

        # ----------------------------------------------------------------
        # Parse via unified service - single call regardless of file type.
        # parse_resume_from_upload reads the bytes that were just consumed
        # by await file.read(); we need to re-seek first.
        # ----------------------------------------------------------------
        file.file.seek(0)
        try:
            parsed: ParsedResume = parse_resume_from_upload(file)
        except Exception:
            logger.exception("Resume parsing failed in candidate upload")
            parsed = ParsedResume()

        resume_score, strengths, weaknesses = _calculate_resume_score(parsed)

        resume_url = f"/uploads/resumes/{current_user.user_id}/{unique_filename}"

        profile.resume_url = resume_url
        profile.resume_score = resume_score
        profile.skills = json.dumps(parsed.skills)
        profile.profile_score = _calculate_profile_score(profile)
        profile.updated_at = datetime.utcnow()

        db.commit()

        notification = Notification(
            user_id=current_user.user_id,
            type="resume_analyzed",
            message=f"Your resume has been analyzed. Score: {resume_score:.0f}%",
        )
        db.add(notification)
        db.commit()

        return ResumeUploadResponse(
            resume_url=resume_url,
            resume_score=resume_score,
            skills=parsed.skills,
            strengths=strengths,
            weaknesses=weaknesses,
        )
    finally:
        db.close()


# =========================================================
# Mock Interview Routes
# =========================================================


@router.post("/mock-interview/start", response_model=MockInterviewStartResponse)
async def start_mock_interview(current_user: TokenData = Depends(get_current_user)):
    if current_user.role != Role.CANDIDATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only candidates can access this endpoint")

    db = SessionLocal()
    try:
        profile = db.query(CandidateProfile).filter(
            CandidateProfile.user_id == current_user.user_id
        ).first()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        if profile.mock_interviews_remaining <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No mock interviews remaining. Upgrade to get more.",
            )

        existing_count = db.query(MockInterview).filter(
            MockInterview.candidate_id == profile.id
        ).count()

        session_id = f"mock-{uuid.uuid4().hex}"
        mock_interview = MockInterview(
            candidate_id=profile.id,
            session_id=session_id,
            status="in_progress",
            interview_number=existing_count + 1,
        )
        db.add(mock_interview)

        profile.mock_interviews_remaining -= 1

        db.commit()
        db.refresh(mock_interview)

        return MockInterviewStartResponse(
            session_id=session_id,
            message="Mock interview started. Connect to WebSocket for the interview.",
            mock_interview_id=mock_interview.id,
        )
    finally:
        db.close()


@router.get("/mock-interview/history", response_model=List[MockInterviewResponse])
async def get_mock_interview_history(current_user: TokenData = Depends(get_current_user)):
    if current_user.role != Role.CANDIDATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only candidates can access this endpoint")

    db = SessionLocal()
    try:
        profile = db.query(CandidateProfile).filter(
            CandidateProfile.user_id == current_user.user_id
        ).first()
        if not profile:
            return []

        interviews = (
            db.query(MockInterview)
            .filter(MockInterview.candidate_id == profile.id)
            .order_by(MockInterview.created_at.desc())
            .all()
        )

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
    finally:
        db.close()


@router.get("/mock-interview/{interview_id}", response_model=MockInterviewResponse)
async def get_mock_interview(
    interview_id: int,
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.role != Role.CANDIDATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only candidates can access this endpoint")

    db = SessionLocal()
    try:
        profile = db.query(CandidateProfile).filter(
            CandidateProfile.user_id == current_user.user_id
        ).first()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        interview = db.query(MockInterview).filter(
            MockInterview.id == interview_id,
            MockInterview.candidate_id == profile.id,
        ).first()
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
    finally:
        db.close()


# =========================================================
# Notification Routes
# =========================================================


@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(current_user: TokenData = Depends(get_current_user)):
    if current_user.role != Role.CANDIDATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only candidates can access this endpoint")

    db = SessionLocal()
    try:
        notifications = (
            db.query(Notification)
            .filter(Notification.user_id == current_user.user_id)
            .order_by(Notification.created_at.desc())
            .limit(50)
            .all()
        )

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
    finally:
        db.close()


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.role != Role.CANDIDATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only candidates can access this endpoint")

    db = SessionLocal()
    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.user_id,
        ).first()
        if not notification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

        notification.is_read = True
        db.commit()

        return {"message": "Notification marked as read"}
    finally:
        db.close()


# =========================================================
# Dashboard Route
# =========================================================


@router.get("/dashboard", response_model=DashboardResponse)
async def get_candidate_dashboard(current_user: TokenData = Depends(get_current_user)):
    if current_user.role != Role.CANDIDATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only candidates can access this endpoint")

    db = SessionLocal()
    try:
        profile = db.query(CandidateProfile).filter(
            CandidateProfile.user_id == current_user.user_id
        ).first()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        recent_activity = []

        recent_interview = (
            db.query(MockInterview)
            .filter(
                MockInterview.candidate_id == profile.id,
                MockInterview.status == "completed",
            )
            .order_by(MockInterview.completed_at.desc())
            .first()
        )

        if recent_interview:
            recent_activity.append(
                f"Mock Interview #{recent_interview.interview_number} completed - Score: {recent_interview.score:.0f}"
            )

        if profile.resume_url:
            recent_activity.append("Resume analyzed")

        if profile.profile_score and profile.profile_score >= 50:
            recent_activity.append("Profile updated")

        completed_interviews = (
            db.query(MockInterview)
            .filter(
                MockInterview.candidate_id == profile.id,
                MockInterview.status == "completed",
                MockInterview.score.isnot(None),
            )
            .all()
        )

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
    finally:
        db.close()

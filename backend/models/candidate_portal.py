"""
Candidate Portal Models

Database models for the candidate portal including:
- CandidateProfile: Candidate profile information
- MockInterview: AI mock interview records
- Notification: User notifications
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, Boolean
from backend.infrastructure.database.database import Base


class CandidateProfile(Base):
    """Candidate profile information."""
    __tablename__ = "candidate_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    skills = Column(Text, nullable=True)  # JSON string of skills list
    experience_years = Column(Integer, nullable=True)
    education = Column(Text, nullable=True)
    resume_url = Column(String, nullable=True)
    resume_score = Column(Float, nullable=True)
    interview_score = Column(Float, nullable=True)
    profile_score = Column(Float, nullable=True)
    github_url = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    mock_interviews_remaining = Column(Integer, nullable=False, default=3)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MockInterview(Base):
    """AI mock interview record."""
    __tablename__ = "mock_interviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidate_profiles.id"), nullable=False)
    session_id = Column(String, nullable=False)
    score = Column(Float, nullable=True)
    technical_score = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=True)
    reasoning_score = Column(Float, nullable=True)
    evaluation = Column(Text, nullable=True)  # JSON string of evaluation
    transcript = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="in_progress")  # in_progress, completed
    interview_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)


class Notification(Base):
    """User notifications."""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False)  # interview_invite, report_ready, etc.
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text

from backend.infrastructure.database.database import Base


class ExperienceLevel(str, Enum):
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"


class JobPostStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"
    ARCHIVED = "archived"


class CandidateStatus(str, Enum):
    INVITED = "invited"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class JobPost(Base):
    __tablename__ = "job_posts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    experience_level = Column(String, nullable=False, default=ExperienceLevel.MID.value)
    status = Column(String, nullable=False, default=JobPostStatus.DRAFT.value)
    ai_interview_enabled = Column(String, nullable=False, default="false")
    interview_limit = Column(Integer, nullable=True)  # Budget-based limit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String, nullable=True)


class JobSkill(Base):
    __tablename__ = "job_skills"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_post_id = Column(String, ForeignKey("job_posts.id"), nullable=False)
    skill_name = Column(String, nullable=False)
    is_required = Column(String, nullable=False, default="true")
    proficiency_level = Column(String, nullable=True)  # beginner, intermediate, advanced


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    role = Column(String, nullable=False)
    resume_url = Column(String, nullable=True)
    status = Column(String, nullable=False, default=CandidateStatus.INVITED.value)
    job_post_id = Column(String, ForeignKey("job_posts.id"), nullable=True)
    interview_link = Column(String, nullable=True)
    interview_link_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False)
    role = Column(String, nullable=False)
    overall_score = Column(Float, nullable=True)
    technical_score = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=True)
    problem_solving_score = Column(Float, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_id = Column(String, ForeignKey("interviews.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)


class InterviewReplaySegment(Base):
    __tablename__ = "interview_replay_segments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_id = Column(String, ForeignKey("interviews.id"), nullable=False)
    question = Column(Text, nullable=False)
    transcript = Column(Text, nullable=True)
    audio_url = Column(String, nullable=True)
    score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

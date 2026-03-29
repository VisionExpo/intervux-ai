from __future__ import annotations

import base64
import os
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

import docx
import pdfplumber
import spacy
from fastapi import UploadFile
from pydantic import BaseModel, Field

from backend.utils.logger import get_logger

from .models import CandidateProfile

logger = get_logger(__name__)

try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    # Fall back to a blank model when language package is not available.
    nlp = spacy.blank("en")


# ---------------------------------------------------------------------------
# Text extraction + entity extraction (legacy-compatible primitives)
# ---------------------------------------------------------------------------


def parse_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    with pdfplumber.open(file_path) as pdf:
        chunks = []
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text:
                chunks.append(page_text)
    return "\n".join(chunks)


def parse_docx(file_path: str) -> str:
    """Extract text from a DOCX file."""
    doc = docx.Document(file_path)
    lines = [para.text for para in doc.paragraphs if para.text]
    return "\n".join(lines)


def parse_txt(file_path: str) -> str:
    """Read text from a TXT file."""
    with open(file_path, "r", encoding="utf-8") as file_handle:
        return file_handle.read()


def parse_resume(file_path: str, file_type: str) -> str:
    """Legacy parser: parse resume file and return extracted text."""
    normalized_type = (file_type or "").lower().strip(".")
    if normalized_type == "pdf":
        return parse_pdf(file_path)
    if normalized_type == "docx":
        return parse_docx(file_path)
    if normalized_type == "txt":
        return parse_txt(file_path)
    raise ValueError(f"Unsupported file type: {file_type}")


def extract_entities(text: str) -> CandidateProfile:
    """Extract basic entities and keyword skills from resume text."""
    doc = nlp(text or "")
    profile = CandidateProfile()

    for ent in doc.ents:
        if ent.label_ == "PERSON" and not profile.name:
            profile.name = ent.text
        elif ent.label_ == "ORG":
            profile.companies.append(ent.text)

    skills = ["python", "docker", "aws", "machine learning", "kubernetes", "javascript"]
    text_lower = (text or "").lower()
    for skill in skills:
        if skill in text_lower:
            profile.skills.append(skill)

    return profile


# ---------------------------------------------------------------------------
# Unified output schema
# ---------------------------------------------------------------------------


class ParsedProject(BaseModel):
    title: str = ""
    tech_stack: List[str] = Field(default_factory=list)
    description: str = ""


class ParsedExperience(BaseModel):
    role: str = ""
    company: str = ""
    duration: str = ""
    description: str = ""


class ParsedResume(BaseModel):
    """Canonical schema produced by every parser backend."""

    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    projects: List[ParsedProject] = Field(default_factory=list)
    experience: List[ParsedExperience] = Field(default_factory=list)
    education: List[str] = Field(default_factory=list)
    companies: List[str] = Field(default_factory=list)
    raw_text: str = ""
    parser_used: str = "unknown"

    def to_interview_profile(self) -> dict:
        """Return a dict that maps directly onto ResumeData/InterviewState.profile."""
        return {
            "name": self.name,
            "skills": self.skills,
            "projects": [
                {
                    "title": p.title,
                    "tech_stack": p.tech_stack,
                    "description": p.description,
                }
                for p in self.projects
            ],
        }

    def is_empty(self) -> bool:
        """True if the parser produced no usable signal."""
        return not self.skills and not self.name and not self.experience


# ---------------------------------------------------------------------------
# Strategy ABC
# ---------------------------------------------------------------------------


class ResumeParserStrategy(ABC):
    """Abstract base for resume parser backends."""

    @abstractmethod
    def parse_file(self, file_path: str) -> ParsedResume:
        """Parse a resume from a local filesystem path."""

    def parse_bytes(self, file_name: str, file_bytes: bytes) -> ParsedResume:
        """Parse bytes by writing a temporary file and delegating to parse_file()."""
        suffix = Path(file_name).suffix if file_name else ".pdf"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
        try:
            return self.parse_file(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


# ---------------------------------------------------------------------------
# Gemini implementation
# ---------------------------------------------------------------------------


class GeminiResumeParser(ResumeParserStrategy):
    """Calls the Gemini vision model via ResumeParser from agent_ocr.py."""

    def parse_file(self, file_path: str) -> ParsedResume:
        from backend.core.agent_ocr import ResumeParser as _GeminiParser  # lazy import

        raw: dict = _GeminiParser().parse(file_path)
        return _gemini_dict_to_parsed_resume(raw)


def _gemini_dict_to_parsed_resume(raw: dict) -> ParsedResume:
    """Normalize Gemini JSON payload -> ParsedResume."""
    if not isinstance(raw, dict):
        raw = {}

    contact = raw.get("contact") or {}
    if not isinstance(contact, dict):
        contact = {}

    skills = [s for s in (raw.get("skills") or []) if isinstance(s, str)]

    projects: List[ParsedProject] = []
    for project in raw.get("projects") or []:
        if not isinstance(project, dict):
            continue
        tech = [tech_item for tech_item in (project.get("tech_stack") or []) if isinstance(tech_item, str)]
        projects.append(
            ParsedProject(
                title=str(project.get("title") or ""),
                tech_stack=tech,
                description=str(project.get("description") or ""),
            )
        )

    experience: List[ParsedExperience] = []
    for exp in raw.get("experience") or []:
        if not isinstance(exp, dict):
            continue
        experience.append(
            ParsedExperience(
                role=str(exp.get("role") or ""),
                company=str(exp.get("company") or ""),
                duration=str(exp.get("duration") or ""),
                description=str(exp.get("description") or ""),
            )
        )

    education_raw = raw.get("education") or []
    if isinstance(education_raw, list):
        education = [str(entry) for entry in education_raw if entry]
    else:
        education = [str(education_raw)] if education_raw else []

    return ParsedResume(
        name=raw.get("name") if isinstance(raw.get("name"), str) else None,
        email=contact.get("email") if isinstance(contact.get("email"), str) else None,
        phone=contact.get("phone") if isinstance(contact.get("phone"), str) else None,
        linkedin=contact.get("linkedin") if isinstance(contact.get("linkedin"), str) else None,
        skills=skills,
        projects=projects,
        experience=experience,
        education=education,
        parser_used="gemini",
    )


# ---------------------------------------------------------------------------
# Text / spaCy implementation
# ---------------------------------------------------------------------------


class TextResumeParser(ResumeParserStrategy):
    """Uses pdfplumber / python-docx + spaCy for text extraction."""

    def parse_file(self, file_path: str) -> ParsedResume:
        extension = Path(file_path).suffix.lower().strip(".")
        try:
            text = parse_resume(file_path, extension)
        except Exception:
            logger.exception("Text parser failed to extract text from %s", file_path)
            text = ""

        profile = extract_entities(text)

        return ParsedResume(
            name=profile.name,
            email=profile.email,
            phone=profile.phone,
            skills=list(profile.skills),
            companies=list(profile.companies),
            education=list(profile.education),
            raw_text=text,
            parser_used="text",
        )


# ---------------------------------------------------------------------------
# Service (primary + optional fallback)
# ---------------------------------------------------------------------------


class ResumeParserService:
    """Select backend from env and optionally fallback on empty/failed result."""

    def __init__(self) -> None:
        backend = os.getenv("RESUME_PARSER_BACKEND", "gemini").strip().lower()
        fallback_enabled = os.getenv("RESUME_PARSER_FALLBACK", "true").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

        if backend == "text":
            self._primary: ResumeParserStrategy = TextResumeParser()
            self._fallback: Optional[ResumeParserStrategy] = (
                GeminiResumeParser() if fallback_enabled else None
            )
        else:
            self._primary = GeminiResumeParser()
            self._fallback = TextResumeParser() if fallback_enabled else None

        logger.info(
            "ResumeParserService initialized",
            extra={
                "extra_data": {
                    "primary": backend,
                    "fallback_enabled": fallback_enabled,
                }
            },
        )

    def parse_file(self, file_path: str) -> ParsedResume:
        try:
            result = self._primary.parse_file(file_path)
            if not result.is_empty():
                return result
            raise ValueError("Primary parser returned empty result")
        except Exception as exc:
            logger.warning(
                "Primary resume parser failed; trying fallback",
                extra={"extra_data": {"error": str(exc), "file": file_path}},
            )
            if self._fallback is not None:
                try:
                    return self._fallback.parse_file(file_path)
                except Exception:
                    logger.exception("Fallback resume parser also failed for %s", file_path)
            return ParsedResume(parser_used="failed")

    def parse_bytes(self, file_name: str, file_bytes: bytes) -> ParsedResume:
        try:
            result = self._primary.parse_bytes(file_name, file_bytes)
            if not result.is_empty():
                return result
            raise ValueError("Primary parser returned empty result")
        except Exception as exc:
            logger.warning(
                "Primary resume parser (bytes) failed; trying fallback",
                extra={"extra_data": {"error": str(exc), "file_name": file_name}},
            )
            if self._fallback is not None:
                try:
                    return self._fallback.parse_bytes(file_name, file_bytes)
                except Exception:
                    logger.exception("Fallback resume parser (bytes) also failed")
            return ParsedResume(parser_used="failed")


# Lazy singleton to avoid import-time model/client initialization.
_service: Optional[ResumeParserService] = None


def _get_service() -> ResumeParserService:
    global _service
    if _service is None:
        _service = ResumeParserService()
    return _service


# ---------------------------------------------------------------------------
# Public API - preferred by call sites
# ---------------------------------------------------------------------------


def parse_resume_from_path(file_path: str) -> ParsedResume:
    """Parse a resume from filesystem path."""
    return _get_service().parse_file(file_path)


def parse_resume_from_bytes(file_name: str, file_bytes: bytes) -> ParsedResume:
    """Parse a resume from raw bytes."""
    return _get_service().parse_bytes(file_name, file_bytes)


def parse_resume_from_b64(file_name: str, file_bytes_b64: str) -> ParsedResume:
    """Parse a resume from a base64-encoded payload."""
    decoded = base64.b64decode(file_bytes_b64)
    return parse_resume_from_bytes(file_name, decoded)


def parse_resume_from_upload(file: UploadFile) -> ParsedResume:
    """Parse a resume from FastAPI UploadFile and reset stream pointer."""
    file_bytes = file.file.read()
    file.file.seek(0)
    return parse_resume_from_bytes(file.filename or "", file_bytes)


# ---------------------------------------------------------------------------
# Legacy compatibility wrappers (used by existing Celery/routes)
# ---------------------------------------------------------------------------


def parse_resume_service(resume_path: str) -> Dict[str, Any]:
    """Celery-compatible output wrapper over the unified parser."""
    parsed = parse_resume_from_path(resume_path)
    return {
        "text": parsed.raw_text,
        "profile": {
            "name": parsed.name,
            "email": parsed.email,
            "phone": parsed.phone,
            "skills": parsed.skills,
            "experience_years": None,
            "companies": parsed.companies,
            "education": parsed.education,
            "projects": [p.title for p in parsed.projects],
        },
        "parser_used": parsed.parser_used,
    }


def parse_resume_from_text_service(resume_text: str, file_type: str = "txt") -> Dict[str, Any]:
    """Legacy text-only parser service retained for worker compatibility."""
    profile = extract_entities(resume_text or "")
    return {
        "text": resume_text or "",
        "file_type": file_type,
        "profile": profile.model_dump(),
        "parser_used": "text",
    }

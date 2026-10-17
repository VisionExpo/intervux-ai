"""
Legacy Resume Upload Route

This route previously called the text parser directly.
It now goes through the unified ResumeParserService so it benefits
from the same Gemini primary + text fallback chain as the rest of the platform.
"""

from typing import List, Optional

from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.core.security.jwt_service import Role, TokenData, get_current_user
from backend.services.resume_parser_service import parse_resume_from_upload
import asyncio

router = APIRouter()
RESUME_ROOT = Path(__file__).resolve().parents[2] / "uploads" / "resumes"


class ResumeProfile(BaseModel):
    """Response schema for the legacy upload endpoint."""

    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = []
    companies: List[str] = []
    education: List[str] = []
    parser_used: str = "unknown"


@router.post("/upload", response_model=ResumeProfile)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Upload a resume file and return extracted entities.

    Supports PDF, DOCX, and TXT. Uses the unified ResumeParserService
    (Gemini vision primary, pdfplumber+spaCy fallback).
    """
    if current_user.role != Role.CANDIDATE:
        raise HTTPException(status_code=403, detail="Only candidates can upload resumes")

    allowed_extensions = {".pdf", ".docx", ".txt"}
    filename = file.filename or ""
    file_ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if f".{file_ext}" not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a PDF, DOCX, or TXT file.",
        )

    try:
        parsed = await asyncio.to_thread(parse_resume_from_upload, file)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {exc}") from exc

    return ResumeProfile(
        name=parsed.name,
        email=parsed.email,
        phone=parsed.phone,
        skills=parsed.skills,
        companies=parsed.companies,
        education=parsed.education,
        parser_used=parsed.parser_used,
    )


@router.get("/files/{user_id}/{filename}")
async def get_resume_file(
    user_id: str,
    filename: str,
    current_user: TokenData = Depends(get_current_user),
):
    """Return a resume only to its owner or an administrator."""
    if current_user.role != Role.ADMIN and (
        current_user.role != Role.CANDIDATE or current_user.user_id != user_id
    ):
        raise HTTPException(status_code=404, detail="Resume not found")

    if Path(filename).name != filename or filename in {".", ".."}:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume_root = RESUME_ROOT.resolve()
    resume_path = (resume_root / user_id / filename).resolve()
    if resume_root not in resume_path.parents or not resume_path.is_file():
        raise HTTPException(status_code=404, detail="Resume not found")

    return FileResponse(resume_path, filename=filename)

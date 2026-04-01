"""
Legacy Resume Upload Route

This route previously called the text parser directly.
It now goes through the unified ResumeParserService so it benefits
from the same Gemini primary + text fallback chain as the rest of the platform.
"""

from typing import List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from backend.services.resume_parser_service import parse_resume_from_upload
import asyncio

router = APIRouter()


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
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload a resume file and return extracted entities.

    Supports PDF, DOCX, and TXT. Uses the unified ResumeParserService
    (Gemini vision primary, pdfplumber+spaCy fallback).
    """
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

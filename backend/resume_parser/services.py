from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import docx
import pdfplumber
import spacy

from .models import CandidateProfile

try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    # Fall back to a blank model when language package is not available.
    nlp = spacy.blank("en")


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
    """Parse a resume file and return extracted text."""
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


def parse_resume_service(resume_path: str) -> Dict[str, Any]:
    """Celery-friendly parser used by worker tasks."""
    extension = Path(resume_path).suffix.lower().strip(".")
    text = parse_resume(resume_path, extension)
    profile = extract_entities(text)
    return {
        "text": text,
        "profile": profile.model_dump(),
    }


def parse_resume_from_text_service(resume_text: str, file_type: str = "txt") -> Dict[str, Any]:
    """Parse already-extracted resume text and return profile payload."""
    profile = extract_entities(resume_text or "")
    return {
        "text": resume_text or "",
        "file_type": file_type,
        "profile": profile.model_dump(),
    }

"""
Unified resume parser service exports.

This shim keeps service-style imports stable:
    from backend.services.resume_parser_service import parse_resume_from_b64
"""

from backend.ai.resume_parser.services import (  # noqa: F401
    ParsedExperience,
    ParsedProject,
    ParsedResume,
    parse_resume_from_b64,
    parse_resume_from_bytes,
    parse_resume_from_path,
    parse_resume_from_upload,
)


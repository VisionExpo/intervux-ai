"""
Celery Tasks for Intervux AI.

Resume-related tasks now go through the unified ResumeParserService
instead of calling backend.resume_parser.services directly.
"""

import os
import base64
from datetime import datetime
from typing import Any, Dict, Optional

from celery import Task

from backend.core.celery_app import celery_app
from backend.core.logging.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# Base Task with Error Handling
# =============================================================================


class ErrorHandlingTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {task_id} failed: {exc}")
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        logger.warning(f"Task {task_id} retrying: {exc}")
        super().on_retry(exc, task_id, args, kwargs, einfo)


# =============================================================================
# Audio Processing Offloading
# =============================================================================

@celery_app.task(bind=True, base=ErrorHandlingTask, name="backend.core.celery_tasks.transcribe_audio_task")
def transcribe_audio_task(self, b64_audio: str, suffix: str) -> str:
    """CPU-bound audio transcription."""
    from backend.services.stt_service import transcribe_audio_bytes
    audio_bytes = base64.b64decode(b64_audio)
    return transcribe_audio_bytes(audio_bytes, suffix)


@celery_app.task(bind=True, base=ErrorHandlingTask, name="backend.core.celery_tasks.synthesize_tts_task")
def synthesize_tts_task(self, text: str) -> Dict[str, Any]:
    """CPU/IO-bound audio synthesis. Returns b64 encoded audio."""
    from backend.services.tts_service import synthesize_speech_with_visemes
    from backend.services.viseme_service import VisemeService
    import wave, io

    vs = VisemeService()
    audio_bytes, visemes = synthesize_speech_with_visemes(text)

    if not visemes:
        duration = 0
        try:
            with wave.open(io.BytesIO(audio_bytes), "rb") as w:
                duration = max(int((w.getnframes() / w.getframerate()) * 1000), 0)
        except Exception:
            pass
        visemes = vs.generate_timeline(duration)

    return {
        "audio_b64": base64.b64encode(audio_bytes).decode('ascii') if audio_bytes else "",
        "visemes": visemes
    }


# =============================================================================
# Resume Parsing Tasks
# =============================================================================


@celery_app.task(
    bind=True,
    base=ErrorHandlingTask,
    name="backend.core.celery_tasks.parse_resume",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_kwargs={"max_retries": 3},
)
def parse_resume(self, resume_path: str, candidate_id: Optional[str] = None) -> Dict[str, Any]:
    logger.info(f"Parsing resume: {resume_path}")

    try:
        from backend.services.resume_parser_service import parse_resume_from_path

        parsed = parse_resume_from_path(resume_path)

        result: Dict[str, Any] = {
            "name": parsed.name,
            "email": parsed.email,
            "phone": parsed.phone,
            "skills": parsed.skills,
            "experience": [e.model_dump() for e in parsed.experience],
            "education": parsed.education,
            "projects": [p.model_dump() for p in parsed.projects],
            "companies": parsed.companies,
            "parser_used": parsed.parser_used,
        }

        if candidate_id:
            result["candidate_id"] = candidate_id

        return result
    except Exception as e:
        logger.error(f"Failed to parse resume: {e}")
        raise


@celery_app.task(
    bind=True,
    base=ErrorHandlingTask,
    name="backend.core.celery_tasks.parse_resume_from_text",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def parse_resume_from_text(self, resume_text: str, file_type: str = "txt") -> Dict[str, Any]:
    logger.info(f"Parsing resume from text, type: {file_type}")

    try:
        from backend.ai.resume_parser.services import extract_entities
        profile = extract_entities(resume_text or "")

        return {
            "name": profile.name,
            "email": profile.email,
            "phone": profile.phone,
            "skills": list(profile.skills),
            "companies": list(profile.companies),
            "education": list(profile.education),
            "text": resume_text or "",
            "file_type": file_type,
            "parser_used": "text",
        }
    except Exception as e:
        logger.error(f"Failed to parse resume from text: {e}")
        raise


# =============================================================================
# Evaluation Tasks
# =============================================================================


@celery_app.task(
    bind=True,
    base=ErrorHandlingTask,
    name="backend.core.celery_tasks.generate_evaluation",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 2},
)
def generate_evaluation(self, interview_id: str) -> Dict[str, Any]:
    logger.info(f"Generating evaluation for interview: {interview_id}")

    try:
        from backend.services.decision_support_service import generate_full_report
        from backend.infrastructure.database.database import AsyncSessionLocal
        # Note: Since this is purely for the task runner, to query DB we need asyncio loop
        # We will stub this for the architecture demo as moving to AsyncSession alters this entirely.
        
        # This was a sync DB call. In async it needs asyncio.run()
        # Due to refactoring, we'll implement later or bypass.
        return {"report": "Pending Async Port", "interview_id": interview_id}

    except Exception as e:
        logger.error(f"Failed to generate evaluation: {e}")
        raise


@celery_app.task(
    bind=True,
    base=ErrorHandlingTask,
    name="backend.core.celery_tasks.generate_evaluation_async",
)
def generate_evaluation_async(
    self,
    answers: list,
    profile: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    logger.info("Generating evaluation from answers")
    try:
        from backend.services.decision_support_service import generate_full_report
        report = generate_full_report(answers=answers, profile=profile)
        return {"report": report}
    except Exception as e:
        logger.error(f"Failed to generate evaluation: {e}")
        raise


# =============================================================================
# Health Check
# =============================================================================


@celery_app.task(name="backend.core.celery_tasks.health_check")
def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }

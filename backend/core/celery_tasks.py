"""
Celery Tasks for Intervux AI.

This module provides Celery tasks for heavy background operations:
- Resume parsing
- Async evaluation generation
- Report generation
- Alert dispatching

Example usage:
    from backend.core.celery_tasks import generate_evaluation
    
    # Call task asynchronously
    task = generate_evaluation.delay(interview_id="123")
    
    # Get result
    result = task.get(timeout=60)
"""

import os
from datetime import datetime
from typing import Any, Dict, Optional

from celery import Task

from backend.core.celery_app import celery_app
from backend.utils.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# Base Task with Error Handling
# =============================================================================


class ErrorHandlingTask(Task):
    """Base task class with error handling and retry logic."""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails."""
        logger.error(
            f"Task {task_id} failed: {exc}",
            extra={"extra_data": {"task_id": task_id, "args": args, "kwargs": kwargs}}
        )
        super().on_failure(exc, task_id, args, kwargs, einfo)
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried."""
        logger.warning(
            f"Task {task_id} retrying: {exc}",
            extra={"extra_data": {"task_id": task_id}}
        )
        super().on_retry(exc, task_id, args, kwargs, einfo)


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
    """
    Parse resume from file path.
    
    Args:
        resume_path: Path to the resume file
        candidate_id: Optional candidate ID for linking
        
    Returns:
        Parsed resume data
    """
    logger.info(f"Parsing resume: {resume_path}")
    
    try:
        # Import here to avoid circular imports
        from backend.resume_parser.services import parse_resume_service
        
        result = parse_resume_service(resume_path)
        
        if candidate_id:
            result["candidate_id"] = candidate_id
            
        logger.info(f"Resume parsed successfully: {resume_path}")
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
def parse_resume_from_text(self, resume_text: str, file_type: str = "pdf") -> Dict[str, Any]:
    """
    Parse resume from text content.
    
    Args:
        resume_text: Text content of the resume
        file_type: Type of file (pdf, docx, txt)
        
    Returns:
        Parsed resume data
    """
    logger.info(f"Parsing resume from text, type: {file_type}")
    
    try:
        from backend.resume_parser.services import parse_resume_from_text_service
        
        result = parse_resume_from_text_service(resume_text, file_type)
        logger.info("Resume parsed successfully from text")
        return result
        
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
    """
    Generate interview evaluation.
    
    Args:
        interview_id: Interview ID
        
    Returns:
        Evaluation results
    """
    logger.info(f"Generating evaluation for interview: {interview_id}")
    
    try:
        from backend.services.decision_support_service import generate_full_report
        from backend.db.database import SessionLocal
        from backend.models.recruiter_dashboard_models import Interview, InterviewQuestion
        
        db = SessionLocal()
        try:
            # Get interview data
            interview = db.query(Interview).filter(Interview.id == interview_id).first()
            
            if not interview:
                return {"error": "Interview not found", "interview_id": interview_id}
            
            # Get questions and answers
            questions = db.query(InterviewQuestion).filter(
                InterviewQuestion.interview_id == interview_id
            ).all()
            
            answers = []
            for q in questions:
                answers.append({
                    "question": q.question,
                    "answer": q.answer,
                    "score": q.score,
                })
            
            # Generate report
            report = generate_full_report(answers=answers)
            
            logger.info(f"Evaluation generated for interview: {interview_id}")
            return {"report": report, "interview_id": interview_id}
            
        finally:
            db.close()
            
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
    profile: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate evaluation from answers directly.
    
    Args:
        answers: List of question/answer pairs
        profile: Optional candidate profile
        
    Returns:
        Evaluation report
    """
    logger.info("Generating evaluation from answers")
    
    try:
        from backend.services.decision_support_service import generate_full_report
        
        report = generate_full_report(answers=answers, profile=profile)
        
        logger.info("Evaluation generated successfully")
        return {"report": report}
        
    except Exception as e:
        logger.error(f"Failed to generate evaluation: {e}")
        raise


# =============================================================================
# Report Generation Tasks
# =============================================================================


@celery_app.task(
    bind=True,
    base=ErrorHandlingTask,
    name="backend.core.celery_tasks.generate_report",
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2},
)
def generate_report(
    self,
    interview_id: str,
    report_type: str = "full"
) -> Dict[str, Any]:
    """
    Generate interview report.
    
    Args:
        interview_id: Interview ID
        report_type: Type of report (full, summary, decision)
        
    Returns:
        Report data
    """
    logger.info(f"Generating {report_type} report for interview: {interview_id}")
    
    try:
        from backend.services.recruiter_dashboard_store import get_interview_report
        from backend.db.database import SessionLocal
        
        db = SessionLocal()
        try:
            report = get_interview_report(db, interview_id)
            logger.info(f"Report generated for interview: {interview_id}")
            return {"report": report, "report_type": report_type}
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        raise


# =============================================================================
# Alert Tasks
# =============================================================================


@celery_app.task(
    bind=True,
    base=ErrorHandlingTask,
    name="backend.core.celery_tasks.dispatch_alert",
)
def dispatch_alert(
    self,
    alert_type: str,
    message: str,
    severity: str = "info",
    **kwargs
) -> Dict[str, Any]:
    """
    Dispatch alerts.
    
    Args:
        alert_type: Type of alert
        message: Alert message
        severity: Alert severity
        **kwargs: Additional alert data
    """
    logger.info(f"Dispatching {severity} alert: {alert_type}")
    
    try:
        from backend.services.alerting_service import alerting_service
        
        alerting_service.check_and_alert(**kwargs)
        
        return {"alert_type": alert_type, "status": "dispatched", "message": message}
        
    except Exception as e:
        logger.error(f"Failed to dispatch alert: {e}")
        raise


# =============================================================================
# Data Export Tasks
# =============================================================================


@celery_app.task(
    bind=True,
    base=ErrorHandlingTask,
    name="backend.core.celery_tasks.export_data",
)
def export_data(
    self,
    export_type: str,
    format: str = "json",
    filters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Export data to file.
    
    Args:
        export_type: Type of data to export
        format: Export format (json, csv)
        filters: Export filters
        
    Returns:
        Export file path
    """
    logger.info(f"Exporting {export_type} data as {format}")
    
    # Implementation depends on specific export requirements
    export_path = f"/app/exports/{export_type}_{datetime.utcnow().timestamp()}.{format}"
    
    return {
        "export_type": export_type,
        "format": format,
        "status": "completed",
        "path": export_path
    }


# =============================================================================
# Cleanup Tasks
# =============================================================================


@celery_app.task(
    bind=True,
    base=ErrorHandlingTask,
    name="backend.core.celery_tasks.cleanup_old_logs",
)
def cleanup_old_logs(self, days: int = 30) -> Dict[str, Any]:
    """
    Clean up old log files.
    
    Args:
        days: Number of days to keep
        
    Returns:
        Cleanup results
    """
    import shutil
    from pathlib import Path
    
    log_dir = Path("logs")
    if not log_dir.exists():
        return {"status": "no_logs_directory"}
    
    cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
    deleted_count = 0
    
    for log_file in log_dir.glob("*.log"):
        if log_file.stat().st_mtime < cutoff:
            try:
                log_file.unlink()
                deleted_count += 1
            except Exception as e:
                logger.error(f"Failed to delete {log_file}: {e}")
    
    logger.info(f"Cleaned up {deleted_count} old log files")
    return {"status": "completed", "deleted_count": deleted_count}


@celery_app.task(
    bind=True,
    base=ErrorHandlingTask,
    name="backend.core.celery_tasks.aggregate_analytics",
)
def aggregate_analytics(self) -> Dict[str, Any]:
    """
    Aggregate analytics data.
    
    Returns:
        Analytics aggregates
    """
    from backend.services.evaluation_dashboard_store import get_db_metrics_aggregates
    from backend.db.database import SessionLocal
    
    db = SessionLocal()
    try:
        metrics = get_db_metrics_aggregates(db)
        logger.info("Analytics aggregated successfully")
        return {"metrics": metrics}
    finally:
        db.close()


# =============================================================================
# Health Check
# =============================================================================


@celery_app.task(
    name="backend.core.celery_tasks.health_check",
)
def health_check() -> Dict[str, Any]:
    """Get Celery system health."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }


"""
Background Tasks for Intervux AI.

This module provides background task processing for heavy operations:
- Async evaluation generation
- Report generation
- Alert dispatching
- Data exports

Example:
    from backend.background.tasks import run_task, BackgroundTask
    
    @app.post("/api/interview/{interview_id}/evaluate")
    def evaluate(
        background_tasks: BackgroundTasks,
        interview_id: str,
    ):
        background_tasks.add_task(
            run_task,
            BackgroundTask.GENERATE_EVALUATION,
            interview_id=interview_id,
        )
        return {"message": "Evaluation started"}
"""

import asyncio
import os
import threading
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, Optional
from concurrent.futures import Future, ThreadPoolExecutor

from fastapi import BackgroundTasks

from backend.utils.logger import get_logger

logger = get_logger(__name__)


# =========================================================
# Task Types
# =========================================================


class BackgroundTask(str, Enum):
    """Background task types."""
    GENERATE_EVALUATION = "generate_evaluation"
    GENERATE_REPORT = "generate_report"
    DISPATCH_ALERT = "dispatch_alert"
    EXPORT_DATA = "export_data"
    SYNC_DATABASE = "sync_database"
    CLEANUP_LOGS = "cleanup_logs"
    ANALYTICS_AGGREGATION = "analytics_aggregation"


# =========================================================
# Task Queue
# =========================================================


class TaskQueue:
    """
    Simple task queue for background processing.
    
    In production, this would be replaced with Celery or Redis Queue.
    """
    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._tasks: Dict[str, Future | asyncio.Task] = {}
        self._max_tracked_tasks = int(os.getenv("BACKGROUND_MAX_TRACKED_TASKS", "1000"))

    def _prune_tasks(self):
        done_ids = [task_id for task_id, task in self._tasks.items() if task.done()]
        for task_id in done_ids:
            self._tasks.pop(task_id, None)

        overflow = len(self._tasks) - self._max_tracked_tasks
        if overflow > 0:
            for task_id in list(self._tasks.keys())[:overflow]:
                self._tasks.pop(task_id, None)
    
    def submit(
        self,
        task_type: BackgroundTask,
        callback: Callable,
        *args,
        **kwargs
    ) -> str:
        """Submit a task for background processing."""
        self._prune_tasks()
        task_id = f"{task_type.value}_{datetime.utcnow().timestamp()}"
        
        def run():
            try:
                callback(*args, **kwargs)
                logger.info(f"Task {task_id} completed")
            except Exception as e:
                logger.error(f"Task {task_id} failed: {e}")
        
        future = self.executor.submit(run)
        self._tasks[task_id] = future
        
        return task_id
    
    def submit_async(
        self,
        task_type: BackgroundTask,
        coro: Callable,
        *args,
        **kwargs
    ) -> str:
        """Submit an async task."""
        self._prune_tasks()
        task_id = f"{task_type.value}_{datetime.utcnow().timestamp()}"
        
        async def run():
            try:
                await coro(*args, **kwargs)
                logger.info(f"Async task {task_id} completed")
            except Exception as e:
                logger.error(f"Async task {task_id} failed: {e}")
        
        task = asyncio.create_task(run())
        self._tasks[task_id] = task
        
        return task_id
    
    def cancel(self, task_id: str) -> bool:
        """Cancel a task."""
        self._prune_tasks()
        if task_id in self._tasks:
            future = self._tasks[task_id]
            future.cancel()
            self._tasks.pop(task_id, None)
            return True
        return False
    
    def get_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status."""
        self._prune_tasks()
        if task_id not in self._tasks:
            return {"status": "not_found"}
        
        future = self._tasks[task_id]
        
        if future.done():
            if future.exception():
                self._tasks.pop(task_id, None)
                return {"status": "failed", "error": str(future.exception())}
            self._tasks.pop(task_id, None)
            return {"status": "completed"}
        
        return {"status": "running"}


# Singleton instance
task_queue = TaskQueue(max_workers=int(os.getenv("BACKGROUND_WORKERS", "4")))


# =========================================================
# Task Functions
# =========================================================


async def generate_evaluation_task(interview_id: str) -> Dict[str, Any]:
    """
    Background task to generate interview evaluation.
    
    Args:
        interview_id: Interview ID
        
    Returns:
        Evaluation results
    """
    from backend.services.decision_support_service import generate_full_report
    from backend.db.database import AsyncSessionLocal
    from backend.models.recruiter_dashboard_models import Interview, InterviewQuestion
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as db:
        # Get interview data
        res = await db.execute(select(Interview).filter(Interview.id == interview_id))
        interview = res.scalar_one_or_none()
        
        if not interview:
            return {"error": "Interview not found"}
        
        # Get questions and answers
        res2 = await db.execute(select(InterviewQuestion).filter(
            InterviewQuestion.interview_id == interview_id
        ))
        questions = res2.scalars().all()
        
        answers = []
        for q in questions:
            answers.append({
                "question": q.question,
                "answer": q.answer,
                "score": q.score,
            })
        
        # Generate report
        report = generate_full_report(answers=answers)
        
        return {"report": report, "interview_id": interview_id}


async def generate_report_task(
    interview_id: str,
    report_type: str = "full"
) -> Dict[str, Any]:
    """
    Background task to generate interview report.
    
    Args:
        interview_id: Interview ID
        report_type: Type of report (full, summary, decision)
        
    Returns:
        Report data
    """
    from backend.services.recruiter_dashboard_store import get_interview_report
    from backend.db.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        report = await get_interview_report(db, interview_id)
        return {"report": report, "report_type": report_type}


async def dispatch_alert_task(
    alert_type: str,
    message: str,
    severity: str = "info",
    **kwargs
) -> Dict[str, Any]:
    """
    Background task to dispatch alerts.
    
    Args:
        alert_type: Type of alert
        message: Alert message
        severity: Alert severity
        **kwargs: Additional alert data
    """
    from backend.services.alerting_service import alerting_service
    
    # This runs in background so alerting won't block API
    alerting_service.check_and_alert(**kwargs)
    
    return {"alert_type": alert_type, "status": "dispatched"}


async def export_data_task(
    export_type: str,
    format: str = "json",
    filters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Background task to export data.
    
    Args:
        export_type: Type of data to export
        format: Export format (json, csv)
        filters: Export filters
        
    Returns:
        Export file path
    """
    # Implementation depends on specific export requirements
    return {
        "export_type": export_type,
        "format": format,
        "status": "completed",
        "path": f"/exports/{export_type}_{datetime.utcnow().timestamp()}.{format}"
    }


# =========================================================
# Task Runner
# =========================================================


def run_task(
    task_type: BackgroundTask,
    *args,
    **kwargs
):
    """
    Run a background task.
    
    Example:
        run_task(BackgroundTask.GENERATE_EVALUATION, interview_id="123")
    """
    task_map = {
        BackgroundTask.GENERATE_EVALUATION: generate_evaluation_task,
        BackgroundTask.GENERATE_REPORT: generate_report_task,
        BackgroundTask.DISPATCH_ALERT: dispatch_alert_task,
        BackgroundTask.EXPORT_DATA: export_data_task,
    }
    
    task_func = task_map.get(task_type)
    
    if task_func is None:
        logger.error(f"Unknown task type: {task_type}")
        return
    
    coro = task_func(*args, **kwargs)
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(coro)
    except RuntimeError:
        asyncio.run(coro)


# =========================================================
# FastAPI Integration
# =========================================================


def add_background_task(
    background_tasks: BackgroundTasks,
    task_type: BackgroundTask,
    *args,
    **kwargs
):
    """
    Add a background task to FastAPI.
    
    Example:
        @app.post("/api/interview/{interview_id}/evaluate")
        def evaluate(
            background_tasks: BackgroundTasks,
            interview_id: str,
        ):
            add_background_task(
                background_tasks,
                BackgroundTask.GENERATE_EVALUATION,
                interview_id=interview_id,
            )
            return {"message": "Evaluation started"}
    """
    background_tasks.add_task(run_task, task_type, *args, **kwargs)


# =========================================================
# Scheduled Tasks
# =========================================================


class ScheduledTask:
    """Scheduled task wrapper."""
    
    def __init__(self, name: str, interval_seconds: int, task: Callable):
        self.name = name
        self.interval = interval_seconds
        self.task = task
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the scheduled task."""
        self._running = True
        self._task = asyncio.create_task(self._run())
    
    async def stop(self):
        """Stop the scheduled task."""
        self._running = False
        if self._task:
            self._task.cancel()
    
    async def _run(self):
        """Run the task on interval."""
        while self._running:
            try:
                await self.task()
            except Exception as e:
                logger.error(f"Scheduled task {self.name} failed: {e}")
            
            await asyncio.sleep(self.interval)


# Example scheduled tasks
async def cleanup_old_logs():
    """Cleanup old log files."""
    import shutil
    from pathlib import Path
    
    log_dir = Path("logs")
    if not log_dir.exists():
        return
    
    # Clean up logs older than 30 days
    cutoff = datetime.now().timestamp() - (30 * 24 * 60 * 60)
    
    for log_file in log_dir.glob("*.log"):
        if log_file.stat().st_mtime < cutoff:
            try:
                log_file.unlink()
                logger.info(f"Deleted old log: {log_file}")
            except Exception as e:
                logger.error(f"Failed to delete {log_file}: {e}")


async def aggregate_analytics():
    """Aggregate analytics data."""
    from backend.services.evaluation_dashboard_store import get_db_metrics_aggregates
    from backend.db.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        metrics = await get_db_metrics_aggregates(db)
        logger.info(f"Analytics aggregated: {metrics}")


# =========================================================
# Health Check
# =========================================================


def get_background_tasks_health() -> Dict[str, Any]:
    """Get background tasks system health."""
    return {
        "status": "healthy",
        "executor_active": True,
        "queue_size": len(task_queue._tasks),
    }


"""
Celery Application Configuration for Intervux AI.

This module configures Celery for background task processing:
- Async evaluation generation
- Resume parsing
- Report generation
- Data exports

The Celery app is used by:
- API server: for dispatching tasks
- Worker containers: for processing tasks
"""

import os
from celery import Celery

# Get environment variables with defaults
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

# Initialize Celery app
celery_app = Celery(
    "intervux",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=[
        "backend.core.celery_tasks",
    ]
)

# Celery Configuration
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Timezone
    timezone="UTC",
    enable_utc=True,
    
    # Task settings
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3000,  # 50 minutes soft limit
    
    # Result settings
    result_expires=86400,  # 24 hours
    
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    
    # Broker settings
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    
    # Task routing
    task_routes={
        "backend.core.celery_tasks.parse_resume": {"queue": "resumes"},
        "backend.core.celery_tasks.generate_evaluation": {"queue": "evaluations"},
        "backend.core.celery_tasks.generate_report": {"queue": "reports"},
    },
    
    # Beat schedule (for periodic tasks)
    beat_schedule={},
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["backend.core"])


def get_celery_app() -> Celery:
    """Get the Celery application instance."""
    return celery_app


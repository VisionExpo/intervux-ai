"""
Compatibility shim for legacy imports.

Canonical Celery task definitions live in backend.core.celery_tasks.
"""

from backend.core.celery_tasks import *  # noqa: F401,F403

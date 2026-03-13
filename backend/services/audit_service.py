"""
Audit Logging Service for Intervux AI.

This module provides:
- Audit log recording
- User action tracking
- Compliance logging

Example:
    from backend.services.audit_service import audit_log, AuditAction
    
    audit_log(
        action=AuditAction.VIEW_INTERVIEW,
        user_id="user-123",
        resource_type="interview",
        resource_id="interview-456",
    )
"""

import json
import os
import threading
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

from backend.utils.logger import get_logger

logger = get_logger(__name__)


# =========================================================
# Audit Actions
# =========================================================


class AuditAction(str, Enum):
    """Audit action types."""
    # Authentication
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    TOKEN_REFRESH = "token_refresh"
    
    # User Management
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    USER_VIEW = "user_view"
    PASSWORD_CHANGE = "password_change"
    
    # Interview
    INTERVIEW_START = "interview_start"
    INTERVIEW_COMPLETE = "interview_complete"
    INTERVIEW_VIEW = "interview_view"
    INTERVIEW_EXPORT = "interview_export"
    INTERVIEW_DELETE = "interview_delete"
    
    # Candidates
    CANDIDATE_CREATE = "candidate_create"
    CANDIDATE_UPDATE = "candidate_update"
    CANDIDATE_VIEW = "candidate_view"
    CANDIDATE_DELETE = "candidate_delete"
    
    # Reports
    REPORT_GENERATE = "report_generate"
    REPORT_VIEW = "report_view"
    REPORT_EXPORT = "report_export"
    
    # Dashboard
    DASHBOARD_VIEW = "dashboard_view"
    METRICS_VIEW = "metrics_view"
    
    # Experiments
    EXPERIMENT_CREATE = "experiment_create"
    EXPERIMENT_VIEW = "experiment_view"
    EXPERIMENT_COMPARE = "experiment_compare"
    EXPERIMENT_DELETE = "experiment_delete"
    
    # Settings
    SETTINGS_VIEW = "settings_view"
    SETTINGS_UPDATE = "settings_update"
    
    # Admin
    ADMIN_ACTION = "admin_action"
    SYSTEM_CONFIG_CHANGE = "system_config_change"


# =========================================================
# Audit Event
# =========================================================


class AuditEvent:
    """Represents a single audit event."""
    
    def __init__(
        self,
        action: str,
        user_id: str,
        user_email: str = "",
        user_role: str = "",
        resource_type: str = "",
        resource_id: str = "",
        details: Optional[Dict[str, Any]] = None,
        ip_address: str = "",
        user_agent: str = "",
        success: bool = True,
    ):
        self.action = action
        self.user_id = user_id
        self.user_email = user_email
        self.user_role = user_role
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.details = details or {}
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.success = success
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "action": self.action,
            "user_id": self.user_id,
            "user_email": self.user_email,
            "user_role": self.user_role,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "success": self.success,
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"))


# =========================================================
# Audit Logger
# =========================================================


class AuditLogger:
    """
    Main audit logging service.
    
    Example:
        audit = AuditLogger()
        
        audit.log(
            action=AuditAction.LOGIN,
            user_id="user-123",
            user_email="user@example.com",
        )
    """
    
    def __init__(self):
        self.enabled = os.getenv("AUDIT_LOG_ENABLED", "true").lower() in {
            "1", "true", "yes", "on"
        }
        self.file_path = os.getenv(
            "AUDIT_LOG_PATH", "logs/audit.jsonl"
        )
        self._lock = threading.Lock()
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
    
    def log(
        self,
        action: str,
        user_id: str,
        user_email: str = "",
        user_role: str = "",
        resource_type: str = "",
        resource_id: str = "",
        details: Optional[Dict[str, Any]] = None,
        ip_address: str = "",
        user_agent: str = "",
        success: bool = True,
    ):
        """
        Log an audit event.
        
        Args:
            action: The action performed
            user_id: ID of the user
            user_email: Email of the user
            user_role: Role of the user
            resource_type: Type of resource affected
            resource_id: ID of the resource
            details: Additional details
            ip_address: Client IP address
            user_agent: Client user agent
            success: Whether the action was successful
        """
        if not self.enabled:
            return
        
        event = AuditEvent(
            action=action,
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
        )
        
        # Write to file
        self._write_event(event)
        
        # Also log to main logger
        logger.info(
            f"Audit: {action}",
            extra={
                "audit": event.to_dict()
            }
        )
    
    def _write_event(self, event: AuditEvent):
        """Write event to JSONL file."""
        with self._lock:
            try:
                with open(self.file_path, "a", encoding="utf-8") as f:
                    f.write(event.to_json() + "\n")
            except Exception:
                logger.exception("Failed to write audit event")
    
    def query(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[Dict[str, Any]]:
        """
        Query audit logs.
        
        Args:
            user_id: Filter by user ID
            action: Filter by action
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum results
            
        Returns:
            List of audit events
        """
        if not os.path.exists(self.file_path):
            return []
        
        events = []
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                
                # Apply filters
                if user_id and event.get("user_id") != user_id:
                    continue
                if action and event.get("action") != action:
                    continue
                if resource_type and event.get("resource_type") != resource_type:
                    continue
                if resource_id and event.get("resource_id") != resource_id:
                    continue
                if start_time:
                    event_time = datetime.fromisoformat(event["timestamp"])
                    if event_time < start_time:
                        continue
                if end_time:
                    event_time = datetime.fromisoformat(event["timestamp"])
                    if event_time > end_time:
                        continue
                
                events.append(event)
                
                if len(events) >= limit:
                    break
        
        return events


# Singleton instance
audit_logger = AuditLogger()


# =========================================================
# Convenience Functions
# =========================================================


def audit_log(
    action: str,
    user_id: str,
    user_email: str = "",
    user_role: str = "",
    resource_type: str = "",
    resource_id: str = "",
    details: Optional[Dict[str, Any]] = None,
    ip_address: str = "",
    user_agent: str = "",
    success: bool = True,
):
    """
    Convenience function to log audit events.
    
    Example:
        audit_log(
            action=AuditAction.INTERVIEW_VIEW,
            user_id="user-123",
            user_email="recruiter@example.com",
            user_role="recruiter",
            resource_type="interview",
            resource_id="interview-456",
        )
    """
    audit_logger.log(
        action=action,
        user_id=user_id,
        user_email=user_email,
        user_role=user_role,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
    )


def get_audit_logs(
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100,
) -> list[Dict[str, Any]]:
    """
    Convenience function to query audit logs.
    
    Example:
        logs = get_audit_logs(
            user_id="user-123",
            action=AuditAction.INTERVIEW_VIEW,
        )
    """
    return audit_logger.query(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
    )


# =========================================================
# FastAPI Middleware
# =========================================================


async def audit_middleware(request, call_next):
    """
    FastAPI middleware for automatic audit logging.
    
    This middleware logs:
    - All API requests (optional, disabled by default)
    - Authentication events
    - Error events
    """
    # This is a placeholder - in production, integrate with FastAPI
    response = await call_next(request)
    return response


"""
Structured Logging for Intervux AI.

This module provides structured JSON logging that integrates
with monitoring systems like Datadog, Splunk, and ELK.

Example:
    from backend.core.logging.structured_logger import StructuredLogger, LogEvent
    
    logger = StructuredLogger()
    
    logger.log(
        event=LogEvent.LLM_REQUEST,
        model="gpt-4",
        latency_ms=1500,
        status="success",
    )
"""

import json
import logging
import os
import sys
import threading
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from backend.core.logging.logger import get_logger

logger = get_logger(__name__)


# =========================================================
# Log Events
# =========================================================


class LogEvent(str, Enum):
    """Standardized log event names."""
    # HTTP Events
    HTTP_REQUEST = "http_request"
    HTTP_RESPONSE = "http_response"
    
    # WebSocket Events
    WS_CONNECT = "ws_connect"
    WS_DISCONNECT = "ws_disconnect"
    WS_MESSAGE = "ws_message"
    
    # LLM Events
    LLM_REQUEST = "llm_request"
    LLM_RESPONSE = "llm_response"
    LLM_ERROR = "llm_error"
    
    # Interview Events
    INTERVIEW_START = "interview_start"
    INTERVIEW_QUESTION = "interview_question"
    INTERVIEW_ANSWER = "interview_answer"
    INTERVIEW_EVALUATION = "interview_evaluation"
    INTERVIEW_COMPLETE = "interview_complete"
    
    # Database Events
    DB_QUERY = "db_query"
    DB_INSERT = "db_insert"
    DB_ERROR = "db_error"
    
    # Authentication Events
    AUTH_LOGIN = "auth_login"
    AUTH_LOGOUT = "auth_logout"
    AUTH_ERROR = "auth_error"
    
    # System Events
    SYSTEM_START = "system_start"
    SYSTEM_SHUTDOWN = "system_shutdown"
    SYSTEM_ERROR = "system_error"


# =========================================================
# Log Levels
# =========================================================


class LogLevel:
    """Log level mappings."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# =========================================================
# Structured Logger
# =========================================================


class StructuredLogger:
    """
    Structured JSON logger for Intervux AI.
    
    Example:
        logger = StructuredLogger()
        
        logger.info(
            event=LogEvent.LLM_REQUEST,
            model="gpt-4",
            latency_ms=1500,
        )
    """
    
    def __init__(self, name: str = "intervux"):
        self.name = name
        self.version = os.getenv("APP_VERSION", "1.0.0")
        self.environment = os.getenv("ENVIRONMENT", "development")
        self._local = threading.local()
    
    def _get_logger(self) -> logging.Logger:
        """Get thread-local logger instance."""
        if not hasattr(self._local, "logger"):
            self._local.logger = logging.getLogger(f"intervux.structured")
            if not self._local.logger.handlers:
                handler = logging.StreamHandler(sys.stdout)
                handler.setFormatter(logging.Formatter("%(message)s"))
                self._local.logger.addHandler(handler)
                self._local.logger.setLevel(logging.INFO)
        return self._local.logger
    
    def _build_log(
        self,
        event: str,
        level: str,
        message: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """Build structured log dict conforming strictly to the observability schema."""
        if not hasattr(self, "_sequence"):
            self._sequence = 0
        self._sequence += 1

        # Extract strict fields from context or kwargs
        context = getattr(self._local, "context", {})
        session_id = kwargs.pop("session_id", context.get("session_id", "unknown"))
        event_id = kwargs.pop("event_id", context.get("event_id", "unknown"))
        module = kwargs.pop("module", context.get("module", "unknown"))
        latency_ms = kwargs.pop("latency_ms", context.get("latency_ms", 0.0))

        log = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "session_id": session_id,
            "event_id": event_id,
            "module": module,
            "event": event,
            "sequence": self._sequence,
            "latency_ms": latency_ms,
            "metadata": {
                "level": level,
                "message": message,
                "service": self.name,
                "version": self.version,
                "environment": self.environment,
                **kwargs
            }
        }
        
        return log
    
    def _write(self, log: Dict[str, Any]):
        """Write log to output."""
        json_log = json.dumps(log, separators=(",", ":"))
        self._get_logger().info(json_log)
    
    def log(
        self,
        event: str,
        message: str = "",
        level: str = LogLevel.INFO,
        **kwargs
    ):
        """
        Log a structured message.
        
        Args:
            event: Event name (use LogEvent enum)
            message: Human-readable message
            level: Log level
            **kwargs: Additional fields to log
        """
        log = self._build_log(event, level, message, **kwargs)
        self._write(log)
    
    def debug(self, event: str, message: str = "", **kwargs):
        """Log debug level message."""
        self.log(event, message, LogLevel.DEBUG, **kwargs)
    
    def info(self, event: str, message: str = "", **kwargs):
        """Log info level message."""
        self.log(event, message, LogLevel.INFO, **kwargs)
    
    def warning(self, event: str, message: str = "", **kwargs):
        """Log warning level message."""
        self.log(event, message, LogLevel.WARNING, **kwargs)
    
    def error(self, event: str, message: str = "", **kwargs):
        """Log error level message."""
        self.log(event, message, LogLevel.ERROR, **kwargs)
    
    def critical(self, event: str, message: str = "", **kwargs):
        """Log critical level message."""
        self.log(event, message, LogLevel.CRITICAL, **kwargs)
    
    # Convenience methods for common events
    
    def log_http_request(
        self,
        method: str,
        path: str,
        status_code: int,
        latency_ms: float,
        user_id: Optional[str] = None,
    ):
        """Log HTTP request."""
        self.info(
            event=LogEvent.HTTP_REQUEST,
            message=f"{method} {path} {status_code}",
            method=method,
            path=path,
            status_code=status_code,
            latency_ms=latency_ms,
            user_id=user_id,
        )
    
    def log_llm_request(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        status: str = "success",
        error: Optional[str] = None,
    ):
        """Log LLM request."""
        self.info(
            event=LogEvent.LLM_REQUEST,
            message=f"LLM {model} {status}",
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            latency_ms=latency_ms,
            status=status,
            error=error,
        )
    
    def log_interview_event(
        self,
        event_type: str,
        session_id: str,
        question_index: Optional[int] = None,
        **kwargs
    ):
        """Log interview event."""
        event_map = {
            "start": LogEvent.INTERVIEW_START,
            "question": LogEvent.INTERVIEW_QUESTION,
            "answer": LogEvent.INTERVIEW_ANSWER,
            "evaluation": LogEvent.INTERVIEW_EVALUATION,
            "complete": LogEvent.INTERVIEW_COMPLETE,
        }
        
        self.info(
            event=event_map.get(event_type, LogEvent.INTERVIEW_START),
            message=f"Interview {event_type}",
            session_id=session_id,
            question_index=question_index,
            **kwargs
        )
    
    def log_auth_event(
        self,
        event_type: str,
        user_id: str,
        email: str,
        success: bool = True,
        error: Optional[str] = None,
    ):
        """Log authentication event."""
        event_map = {
            "login": LogEvent.AUTH_LOGIN,
            "logout": LogEvent.AUTH_LOGOUT,
            "error": LogEvent.AUTH_ERROR,
        }
        
        self.info(
            event=event_map.get(event_type, LogEvent.AUTH_LOGIN),
            message=f"Auth {event_type}",
            user_id=user_id,
            email=email,
            success=success,
            error=error,
        )


# Singleton instance
structured_logger = StructuredLogger()


# =========================================================
# Context Variables
# =========================================================


class LogContext:
    """
    Context manager for adding fields to subsequent logs.
    
    Example:
        with LogContext(user_id="user-123", session_id="sess-456"):
            logger.info("message")  # Will include user_id and session_id
    """
    
    def __init__(self, **kwargs):
        self.fields = kwargs
        self._previous_context = None
    
    def __enter__(self):
        self._previous_context = getattr(self._local, "context", {})
        self._local.context = {**self._previous_context, **self.fields}
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._local.context = self._previous_context


# =========================================================
# Decorator for Automatic Logging
# =========================================================


def log_execution_time(event: str):
    """
    Decorator to automatically log function execution time.
    
    Example:
        @log_execution_time(LogEvent.DB_QUERY)
        def my_function():
            ...
    """
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            start = datetime.now(timezone.utc)
            try:
                result = await func(*args, **kwargs)
                latency = (datetime.now(timezone.utc) - start).total_seconds() * 1000
                structured_logger.info(
                    event=event,
                    message=f"{func.__name__} completed",
                    function=func.__name__,
                    latency_ms=latency,
                    status="success",
                )
                return result
            except Exception as e:
                latency = (datetime.now(timezone.utc) - start).total_seconds() * 1000
                structured_logger.error(
                    event=event,
                    message=f"{func.__name__} failed",
                    function=func.__name__,
                    latency_ms=latency,
                    status="error",
                    error=str(e),
                )
                raise
        
        def sync_wrapper(*args, **kwargs):
            start = datetime.now(timezone.utc)
            try:
                result = func(*args, **kwargs)
                latency = (datetime.now(timezone.utc) - start).total_seconds() * 1000
                structured_logger.info(
                    event=event,
                    message=f"{func.__name__} completed",
                    function=func.__name__,
                    latency_ms=latency,
                    status="success",
                )
                return result
            except Exception as e:
                latency = (datetime.now(timezone.utc) - start).total_seconds() * 1000
                structured_logger.error(
                    event=event,
                    message=f"{func.__name__} failed",
                    function=func.__name__,
                    latency_ms=latency,
                    status="error",
                    error=str(e),
                )
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


# =========================================================
# Integration with Standard Logger
# =========================================================


def setup_structured_logging():
    """
    Setup structured logging as the default.
    
    Call this during application startup.
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add JSON handler
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "message": record.getMessage(),
                "service": "intervux",
            }
            
            # Add extra fields
            if hasattr(record, "extra_data"):
                log_data.update(record.extra_data)
            
            return json.dumps(log_data)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root_logger.addHandler(handler)
    
    logger.info("Structured logging initialized")


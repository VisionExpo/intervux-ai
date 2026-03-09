"""
Session Registry - Global registry for managing active interview sessions.
"""

import asyncio
from typing import Dict, Optional

from backend.sessions.interview_session import InterviewSession
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class SessionRegistry:
    """
    Global registry for managing active interview sessions.
    
    Provides:
    - Session registration/removal
    - Session lookup
    - Active session count
    """

    def __init__(self):
        self._sessions: Dict[str, InterviewSession] = {}
        self._lock = asyncio.Lock()

    async def register(self, session_id: str, session: InterviewSession) -> None:
        """Register a new session."""
        async with self._lock:
            self._sessions[session_id] = session
            logger.info(
                "Session registered",
                extra={"extra_data": {"session_id": session_id, "active_count": len(self._sessions)}}
            )

    async def unregister(self, session_id: str) -> None:
        """Remove a session from registry."""
        async with self._lock:
            removed = self._sessions.pop(session_id, None)
            if removed:
                logger.info(
                    "Session unregistered",
                    extra={"extra_data": {"session_id": session_id, "active_count": len(self._sessions)}}
                )

    def get(self, session_id: str) -> Optional[InterviewSession]:
        """Get session by ID."""
        return self._sessions.get(session_id)

    def get_all(self) -> Dict[str, InterviewSession]:
        """Get all active sessions."""
        return dict(self._sessions)

    @property
    def count(self) -> int:
        """Get number of active sessions."""
        return len(self._sessions)

    async def cleanup_all(self) -> None:
        """Clean up all sessions."""
        async with self._lock:
            for session_id in list(self._sessions.keys()):
                try:
                    session = self._sessions.get(session_id)
                    if session:
                        await session.cleanup()
                except Exception as e:
                    logger.error(f"Error cleaning up session {session_id}: {e}")
            
            self._sessions.clear()


# Global registry instance
_registry: Optional[SessionRegistry] = None


def get_session_registry() -> SessionRegistry:
    """Get the global session registry."""
    global _registry
    if _registry is None:
        _registry = SessionRegistry()
    return _registry


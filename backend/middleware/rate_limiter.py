"""
Rate Limiting Middleware for Intervux AI.

This module provides per-user rate limiting:
- Token-based rate limits
- Role-based rate limits
- IP-based fallback

Example:
    from backend.middleware.rate_limiter import RateLimiter, rate_limit
    
    rate_limiter = RateLimiter()
    
    @app.get("/api/candidates")
    @rate_limit(requests=100, window=60)  # 100 requests per minute
    def get_candidates():
        ...
"""

import os
import threading
import time
from collections import defaultdict
from typing import Callable, Dict, Optional

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware

from backend.auth.jwt_service import Role
from backend.auth.jwt_service import verify_token


# =========================================================
# Rate Limit Configuration
# =========================================================


class RateLimitConfig:
    """Rate limit configuration per role."""
    
    # Default limits (requests per minute)
    DEFAULT = 60
    
    # Role-based limits
    LIMITS = {
        Role.ADMIN: 500,      # 500 requests/min
        Role.RECRUITER: 200,  # 200 requests/min
    }
    
    # Global fallback limits
    GLOBAL_IP_LIMIT = 100   # 100 requests/min per IP
    GLOBAL_WS_LIMIT = 10     # 10 connections/min per IP


# =========================================================
# Rate Limiter
# =========================================================


class RateLimiter:
    """
    Per-user rate limiter using token bucket algorithm.
    
    Example:
        limiter = RateLimiter()
        
        # Check if request is allowed
        if not limiter.is_allowed("user-123"):
            raise HTTPException(429, "Rate limit exceeded")
    """
    
    def __init__(self):
        self.enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() in {
            "1", "true", "yes", "on"
        }
        self.default_limit = int(os.getenv("RATE_LIMIT_DEFAULT", "60"))
        self.cleanup_interval = int(os.getenv("RATE_LIMIT_CLEANUP_INTERVAL", "300"))
        self.window_seconds = 60  # 1 minute window
        
        self._buckets: Dict[str, Dict] = defaultdict(self._create_bucket)
        self._lock = threading.Lock()
        self._last_cleanup = time.time()
    
    def _create_bucket(self) -> Dict:
        """Create a new rate limit bucket."""
        return {
            "count": 0,
            "window_start": time.time(),
        }
    
    def _cleanup_old_buckets(self):
        """Remove old inactive buckets."""
        now = time.time()
        if now - self._last_cleanup < self.cleanup_interval:
            return
        
        with self._lock:
            expired_keys = []
            for key, bucket in self._buckets.items():
                if now - bucket["window_start"] > self.window_seconds * 2:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._buckets[key]
            
            self._last_cleanup = now
    
    def is_allowed(
        self,
        identifier: str,
        limit: Optional[int] = None,
    ) -> bool:
        """
        Check if a request is allowed.
        
        Args:
            identifier: User ID or IP address
            limit: Custom limit (uses default if not provided)
            
        Returns:
            True if request is allowed
        """
        if not self.enabled:
            return True
        
        self._cleanup_old_buckets()
        
        now = time.time()
        
        with self._lock:
            bucket = self._buckets[identifier]
            
            # Check if window has expired
            if now - bucket["window_start"] > self.window_seconds:
                bucket["count"] = 0
                bucket["window_start"] = now
            
            # Get limit
            if limit is None:
                limit = self.default_limit
            
            # Check if limit exceeded
            if bucket["count"] >= limit:
                return False
            
            # Increment counter
            bucket["count"] += 1
            
            return True
    
    def get_limit_info(
        self,
        identifier: str,
        limit: Optional[int] = None,
    ) -> Dict[str, any]:
        """
        Get rate limit information for an identifier.
        
        Args:
            identifier: User ID or IP address
            limit: Custom limit
            
        Returns:
            Dictionary with limit info
        """
        if not self.enabled:
            return {
                "enabled": False,
                "limit": limit or self.default_limit,
                "remaining": limit or self.default_limit,
                "reset": int(time.time()) + self.window_seconds,
            }
        
        with self._lock:
            bucket = self._buckets.get(identifier, self._create_bucket())
            
            if limit is None:
                limit = self.default_limit
            
            remaining = max(0, limit - bucket["count"])
            reset = int(bucket["window_start"] + self.window_seconds)
            
            return {
                "enabled": True,
                "limit": limit,
                "remaining": remaining,
                "reset": reset,
            }
    
    def get_limit_for_role(self, role: str) -> int:
        """Get rate limit for a role."""
        return RateLimitConfig.LIMITS.get(role, self.default_limit)
    
    def reset(self, identifier: str):
        """Reset rate limit for an identifier."""
        with self._lock:
            if identifier in self._buckets:
                del self._buckets[identifier]


# Singleton instance
rate_limiter = RateLimiter()


# =========================================================
# FastAPI Dependency
# =========================================================


def get_rate_limit_identifier(request: Request, user_id: Optional[str] = None) -> str:
    """
    Get rate limit identifier from request.
    
    Uses user_id if authenticated, otherwise falls back to IP.
    """
    if user_id:
        return f"user:{user_id}"
    
    # Fall back to IP
    client_ip = request.client.host if request.client else "unknown"
    return f"ip:{client_ip}"


def rate_limit(
    requests: Optional[int] = None,
    window: int = 60,
):
    """
    FastAPI dependency for rate limiting.
    
    Example:
        @app.get("/api/candidates")
        @rate_limit(requests=100, window=60)
        def get_candidates():
            ...
    
    Args:
        requests: Number of requests allowed in window
        window: Time window in seconds
    """
    def dependency(request: Request, user_id: Optional[str] = None):
        identifier = get_rate_limit_identifier(request, user_id)
        limit = requests or rate_limiter.default_limit
        
        if not rate_limiter.is_allowed(identifier, limit):
            limit_info = rate_limiter.get_limit_info(identifier, limit)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "retry_after": limit_info["reset"] - int(time.time()),
                    "limit": limit_info["limit"],
                    "remaining": 0,
                },
                headers={
                    "X-RateLimit-Limit": str(limit_info["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(limit_info["reset"]),
                    "Retry-After": str(limit_info["reset"] - int(time.time())),
                },
            )
    
    return dependency


# =========================================================
# Middleware
# =========================================================


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting.
    
    Add to app:
        app.add_middleware(RateLimitMiddleware)
    """
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
            if token:
                try:
                    token_data = verify_token(token)
                    request.state.user_id = token_data.user_id
                    request.state.user_role = token_data.role
                except Exception:
                    pass
        
        # Get identifier
        user_id = getattr(request.state, "user_id", None)
        identifier = get_rate_limit_identifier(request, user_id)
        
        # Get limit based on role
        role = getattr(request.state, "user_role", None)
        limit = rate_limiter.get_limit_for_role(role) if role else rate_limiter.default_limit
        
        # Check rate limit
        if not rate_limiter.is_allowed(identifier, limit):
            limit_info = rate_limiter.get_limit_info(identifier, limit)
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": limit_info["reset"] - int(time.time()),
                },
                headers={
                    "X-RateLimit-Limit": str(limit_info["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(limit_info["reset"]),
                },
            )
        
        # Add rate limit headers to response
        response = await call_next(request)
        
        limit_info = rate_limiter.get_limit_info(identifier, limit)
        response.headers["X-RateLimit-Limit"] = str(limit_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(limit_info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(limit_info["reset"])
        
        return response


# =========================================================
# WebSocket Rate Limiting
# =========================================================


class WebSocketRateLimiter:
    """
    Rate limiter for WebSocket connections.
    
    Example:
        ws_limiter = WebSocketRateLimiter()
        
        if not await ws_limiter.is_allowed(client_ip):
            await websocket.close(code=1008)
    """
    
    def __init__(self):
        self.enabled = os.getenv("WS_RATE_LIMIT_ENABLED", "true").lower() in {
            "1", "true", "yes", "on"
        }
        self.connection_limit = int(os.getenv("WS_CONNECTION_LIMIT", "5"))
        self.message_limit = int(os.getenv("WS_MESSAGE_LIMIT", "60"))
        self._connections: Dict[str, int] = defaultdict(int)
        self._messages: Dict[str, int] = defaultdict(int)
        self._lock = threading.Lock()
    
    async def is_allowed(self, identifier: str) -> bool:
        """Check if WebSocket connection is allowed."""
        if not self.enabled:
            return True
        
        with self._lock:
            if self._connections[identifier] >= self.connection_limit:
                return False
            self._connections[identifier] += 1
            return True
    
    async def is_message_allowed(self, identifier: str) -> bool:
        """Check if WebSocket message is allowed."""
        if not self.enabled:
            return True
        
        now = time.time()
        
        with self._lock:
            # Reset if window expired
            if now - self._messages.get(f"{identifier}_window", 0) > 60:
                self._messages[identifier] = 0
                self._messages[f"{identifier}_window"] = now
            
            if self._messages[identifier] >= self.message_limit:
                return False
            
            self._messages[identifier] += 1
            return True
    
    def disconnect(self, identifier: str):
        """Record WebSocket disconnect."""
        with self._lock:
            if self._connections[identifier] > 0:
                self._connections[identifier] -= 1


# Singleton instance
ws_rate_limiter = WebSocketRateLimiter()


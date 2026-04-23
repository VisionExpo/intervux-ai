import time
from typing import Dict, Tuple
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiter for demonstration.
    In production, this should use Redis.
    """
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.clients: Dict[str, list] = {}

    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        # Simple sliding window
        if client_ip not in self.clients:
            self.clients[client_ip] = []
        
        # Clean old requests
        self.clients[client_ip] = [t for t in self.clients[client_ip] if now - t < 60]
        
        if len(self.clients[client_ip]) >= self.requests_per_minute:
            return Response(
                content="Too many requests",
                status_code=HTTP_429_TOO_MANY_REQUESTS
            )
        
        self.clients[client_ip].append(now)
        return await call_next(request)

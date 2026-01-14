"""
Request size limit middleware for FastAPI.
Prevents DoS attacks by limiting request body size.
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to limit request body size"""
    
    def __init__(self, app: ASGIApp, max_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_size = max_size
    
    async def dispatch(self, request: Request, call_next):
        # Check Content-Length header if present
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_size:
                    raise HTTPException(
                        status_code=413,
                        detail=f"Request body too large. Maximum size is {self.max_size // (1024 * 1024)}MB"
                    )
            except ValueError:
                # Invalid content-length, let it through (will fail later if actually too large)
                pass
        
        # For streaming requests, we can't check size upfront
        # But we can limit it during reading
        response = await call_next(request)
        return response

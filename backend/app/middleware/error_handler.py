"""
Global error handler middleware for FastAPI.
Sanitizes error messages in production to prevent information disclosure.
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import os
import logging

logger = logging.getLogger(__name__)

# Check if we're in production
IS_PRODUCTION = os.getenv("ENVIRONMENT") == "production" or os.getenv("NODE_ENV") == "production"


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware to sanitize error messages in production"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            # HTTPException is already a proper error response
            # But we should sanitize the detail in production
            if IS_PRODUCTION and isinstance(e.detail, str):
                # Don't expose internal error details in production
                if e.status_code >= 500:
                    logger.error(f"Internal server error: {e.detail}", exc_info=True)
                    return JSONResponse(
                        status_code=e.status_code,
                        content={"detail": "An internal server error occurred. Please try again later."}
                    )
                # For 4xx errors, we can show the message but sanitize it
                return JSONResponse(
                    status_code=e.status_code,
                    content={"detail": e.detail}
                )
            # In development, show full error
            raise e
        except Exception as e:
            # Catch all other exceptions
            logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
            
            if IS_PRODUCTION:
                return JSONResponse(
                    status_code=500,
                    content={"detail": "An internal server error occurred. Please try again later."}
                )
            else:
                # In development, show the actual error
                return JSONResponse(
                    status_code=500,
                    content={"detail": f"Internal server error: {str(e)}"}
                )

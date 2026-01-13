"""
Rate limiting middleware for FastAPI routes.
Provides dependency functions for checking rate limits on AI endpoints.
"""
import logging
from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.rate_limit_service import rate_limit_service
from app.middleware.auth import get_current_user_required
from app.models.user import User
from app.database import get_session

logger = logging.getLogger(__name__)


def check_ai_rate_limit(endpoint: str):
    """
    Dependency factory to check rate limits for AI endpoints.
    
    Usage:
        @router.post("/analyze")
        async def analyze_recipe(
            request: RecipeRequest,
            user: User = Depends(check_ai_rate_limit("analyze_recipe")),
            session: AsyncSession = Depends(get_session)
        ):
            ...
    
    Args:
        endpoint: Endpoint name (e.g., "analyze_recipe")
    
    Returns:
        Dependency function that:
        - Requires authentication
        - Checks rate limit
        - Raises 429 if limit exceeded
        - Returns user if allowed
    """
    async def rate_limit_check(
        response: Response,
        user: User = Depends(get_current_user_required),
        session: AsyncSession = Depends(get_session)
    ) -> User:
        """
        Check rate limit for the current user and endpoint.
        
        Raises:
            HTTPException 429: If rate limit exceeded
        """
        allowed, current_count, limit = await rate_limit_service.check_rate_limit(
            session, user.id, endpoint
        )
        
        # Calculate remaining calls
        remaining = max(0, limit - current_count)
        
        # Calculate reset time (midnight UTC of next day)
        now = datetime.now(timezone.utc)
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        reset_timestamp = int(tomorrow.timestamp())
        
        # Prepare rate limit headers
        rate_limit_headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_timestamp)
        }
        
        # Add rate limit headers to response (for successful requests)
        response.headers.update(rate_limit_headers)
        
        if not allowed:
            logger.warning(
                f"Rate limit exceeded for user {user.id}, endpoint {endpoint}: "
                f"{current_count}/{limit} calls used"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": f"Daily limit of {limit} calls exceeded for {endpoint}",
                    "current": current_count,
                    "limit": limit,
                    "reset_at": "midnight UTC"
                },
                headers=rate_limit_headers
            )
        
        return user
    
    return rate_limit_check

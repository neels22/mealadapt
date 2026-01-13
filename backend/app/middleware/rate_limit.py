"""
Rate limiting middleware for FastAPI routes.
Provides dependency functions for checking rate limits on AI endpoints.
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.rate_limit_service import rate_limit_service
from app.middleware.auth import get_current_user_required
from app.models.user import User
from app.database import get_session


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
        
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": f"Daily limit of {limit} calls exceeded for {endpoint}",
                    "current": current_count,
                    "limit": limit,
                    "reset_at": "midnight UTC"
                }
            )
        
        return user
    
    return rate_limit_check

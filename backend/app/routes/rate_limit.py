"""
Rate limiting management routes.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Dict

from app.services.rate_limit_service import rate_limit_service
from app.middleware.auth import get_current_user_required
from app.models.user import User
from app.database import get_session

router = APIRouter()


class UsageStatsResponse(BaseModel):
    """Response model for usage statistics"""
    usage: Dict[str, Dict[str, int]]


@router.get("/usage", response_model=UsageStatsResponse)
async def get_usage_stats(
    user: User = Depends(get_current_user_required),
    session: AsyncSession = Depends(get_session)
):
    """
    Get current LLM usage statistics for the authenticated user.
    
    Returns usage stats for all endpoints showing:
    - calls: Number of calls made today
    - limit: Daily limit for the endpoint
    - remaining: Remaining calls available today
    """
    stats = await rate_limit_service.get_usage_stats(session, user.id)
    return UsageStatsResponse(usage=stats)

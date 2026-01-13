"""
Rate limiting service for LLM API calls.
Tracks usage per user per endpoint per day and enforces configurable limits.
"""
import os
from datetime import date, datetime
from typing import Tuple, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.tables import LLMUsage
from dotenv import load_dotenv

load_dotenv()


class RateLimitService:
    """Service for managing rate limits on LLM API calls"""
    
    # Default limits (can be overridden by environment variables)
    DEFAULT_LIMITS = {
        "analyze_recipe": 50,
        "analyze_ingredient_image": 30,
        "suggest_recipes_from_ingredients": 20,
        "extract_ingredients_from_recipes": 30,
        "analyze_ingredients": 40,
    }
    
    def __init__(self):
        """Initialize rate limit service with configurable limits from environment"""
        self.daily_limits = {}
        
        # Map endpoint names to environment variable names
        env_var_map = {
            "analyze_recipe": "LLM_LIMIT_ANALYZE_RECIPE",
            "analyze_ingredient_image": "LLM_LIMIT_ANALYZE_INGREDIENT_IMAGE",
            "suggest_recipes_from_ingredients": "LLM_LIMIT_SUGGEST_RECIPES",
            "extract_ingredients_from_recipes": "LLM_LIMIT_EXTRACT_INGREDIENTS",
            "analyze_ingredients": "LLM_LIMIT_ANALYZE_INGREDIENTS",
        }
        
        # Load limits from environment variables, fallback to defaults
        for endpoint, default_limit in self.DEFAULT_LIMITS.items():
            env_var_name = env_var_map.get(endpoint, f"LLM_LIMIT_{endpoint.upper()}")
            limit = os.getenv(env_var_name)
            if limit:
                try:
                    self.daily_limits[endpoint] = int(limit)
                except ValueError:
                    # Invalid value, use default
                    self.daily_limits[endpoint] = default_limit
            else:
                self.daily_limits[endpoint] = default_limit
    
    async def check_rate_limit(
        self,
        session: AsyncSession,
        user_id: str,
        endpoint: str
    ) -> Tuple[bool, int, int]:
        """
        Check if user has exceeded rate limit for an endpoint.
        
        Args:
            session: Database session
            user_id: User ID
            endpoint: Endpoint name (e.g., "analyze_recipe")
        
        Returns:
            Tuple of (allowed: bool, current_count: int, limit: int)
        """
        if user_id is None:
            raise ValueError("user_id is required for rate limiting")
        
        limit = self.daily_limits.get(endpoint, 10)  # Default 10 if endpoint not configured
        today = date.today()
        
        # Get or create usage record
        stmt = select(LLMUsage).where(
            LLMUsage.user_id == user_id,
            LLMUsage.endpoint == endpoint,
            LLMUsage.date == today
        )
        result = await session.execute(stmt)
        usage = result.scalar_one_or_none()
        
        if usage is None:
            # First call today - create new record
            usage = LLMUsage(
                user_id=user_id,
                endpoint=endpoint,
                date=today,
                call_count=1
            )
            session.add(usage)
            await session.flush()
            return (True, 1, limit)
        
        # Check if limit exceeded
        if usage.call_count >= limit:
            return (False, usage.call_count, limit)
        
        # Increment count
        usage.call_count += 1
        usage.updated_at = datetime.utcnow()
        await session.flush()
        
        return (True, usage.call_count, limit)
    
    async def get_usage_stats(
        self,
        session: AsyncSession,
        user_id: str,
        endpoint: Optional[str] = None
    ) -> Dict[str, Dict[str, int]]:
        """
        Get current usage statistics for a user.
        
        Args:
            session: Database session
            user_id: User ID
            endpoint: Optional endpoint name to filter by
        
        Returns:
            Dictionary mapping endpoint names to usage stats:
            {
                "endpoint_name": {
                    "calls": int,
                    "limit": int,
                    "remaining": int
                }
            }
        """
        today = date.today()
        stmt = select(LLMUsage).where(
            LLMUsage.user_id == user_id,
            LLMUsage.date == today
        )
        if endpoint:
            stmt = stmt.where(LLMUsage.endpoint == endpoint)
        
        result = await session.execute(stmt)
        usages = result.scalars().all()
        
        stats = {}
        
        # Add stats for existing usage records
        for usage in usages:
            limit = self.daily_limits.get(usage.endpoint, 10)
            stats[usage.endpoint] = {
                "calls": usage.call_count,
                "limit": limit,
                "remaining": max(0, limit - usage.call_count)
            }
        
        # If filtering by specific endpoint and no record exists, return zero stats
        if endpoint and endpoint not in stats:
            limit = self.daily_limits.get(endpoint, 10)
            stats[endpoint] = {
                "calls": 0,
                "limit": limit,
                "remaining": limit
            }
        
        return stats


# Singleton instance
rate_limit_service = RateLimitService()

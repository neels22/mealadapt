from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
from enum import Enum
import uuid


class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class PlannedMeal(BaseModel):
    """A meal planned for a specific day and time"""
    id: Optional[int] = None
    plan_id: Optional[str] = None
    recipe_id: str
    date: str  # YYYY-MM-DD format
    meal_type: MealType
    servings: int = 1
    notes: Optional[str] = None
    # Joined from saved_recipes
    dish_name: Optional[str] = None
    analysis: Optional[dict] = None


class AddMealRequest(BaseModel):
    """Request to add a meal to the plan"""
    recipe_id: str
    date: str  # YYYY-MM-DD
    meal_type: MealType
    servings: int = 1
    notes: Optional[str] = None


class UpdateMealRequest(BaseModel):
    """Request to update a planned meal"""
    recipe_id: Optional[str] = None
    date: Optional[str] = None
    meal_type: Optional[MealType] = None
    servings: Optional[int] = None
    notes: Optional[str] = None


class MealPlan(BaseModel):
    """A weekly meal plan"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    week_start: str  # Monday of the week, YYYY-MM-DD
    meals: List[PlannedMeal] = []
    created_at: Optional[datetime] = None


class MealPlanResponse(BaseModel):
    """Response containing a meal plan"""
    id: str
    week_start: str
    meals: List[PlannedMeal] = []
    created_at: Optional[str] = None


class GenerateShoppingFromPlanRequest(BaseModel):
    """Request to generate shopping list from meal plan"""
    list_name: str

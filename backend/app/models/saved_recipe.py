from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid


class SaveRecipeRequest(BaseModel):
    """Request to save a recipe after analysis"""
    dish_name: str
    recipe_text: str
    analysis: dict  # The full RecipeAnalysis object
    tags: List[str] = []
    notes: Optional[str] = None


class UpdateRecipeRequest(BaseModel):
    """Request to update a saved recipe"""
    is_favorite: Optional[bool] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class SavedRecipe(BaseModel):
    """A saved recipe with its analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    dish_name: str
    recipe_text: Optional[str] = None
    analysis: Optional[dict] = None
    is_favorite: bool = False
    notes: Optional[str] = None
    tags: List[str] = []
    created_at: Optional[datetime] = None


class SavedRecipeResponse(BaseModel):
    """Response containing a saved recipe"""
    id: str
    dish_name: str
    recipe_text: Optional[str] = None
    analysis: Optional[dict] = None
    is_favorite: bool = False
    notes: Optional[str] = None
    tags: List[str] = []
    created_at: Optional[str] = None


class SavedRecipesListResponse(BaseModel):
    """Response containing list of saved recipes"""
    recipes: List[SavedRecipeResponse]
    total: int

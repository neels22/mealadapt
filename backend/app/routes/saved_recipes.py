"""
Saved recipes management routes.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.saved_recipe import (
    SaveRecipeRequest,
    UpdateRecipeRequest,
    SavedRecipeResponse,
    SavedRecipesListResponse
)
from app import crud
from app.middleware.auth import get_current_user
from app.models.user import User
from app.database import get_session

router = APIRouter()


def recipe_to_response(recipe) -> SavedRecipeResponse:
    """Convert SQLModel SavedRecipe to Pydantic response"""
    tags = [tag.tag for tag in recipe.tags] if recipe.tags else []
    
    return SavedRecipeResponse(
        id=recipe.id,
        dish_name=recipe.dish_name,
        recipe_text=recipe.recipe_text,
        analysis=recipe.get_analysis(),
        is_favorite=recipe.is_favorite,
        notes=recipe.notes,
        tags=tags,
        created_at=str(recipe.created_at) if recipe.created_at else None
    )


@router.get("/saved", response_model=SavedRecipesListResponse)
async def list_saved_recipes(
    favorites_only: bool = False,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get all saved recipes for the current user"""
    recipes = await crud.get_saved_recipes(session, user.id, favorites_only=favorites_only)
    
    return SavedRecipesListResponse(
        recipes=[recipe_to_response(r) for r in recipes],
        total=len(recipes)
    )


@router.get("/saved/{recipe_id}", response_model=SavedRecipeResponse)
async def get_recipe(
    recipe_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get a single saved recipe by ID"""
    recipe = await crud.get_saved_recipe_by_id(session, recipe_id, user.id)
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    return recipe_to_response(recipe)


@router.post("/saved", response_model=SavedRecipeResponse)
async def save_new_recipe(
    request: SaveRecipeRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Save a new recipe after analysis"""
    recipe_id = str(uuid.uuid4())
    
    recipe = await crud.save_recipe(
        session,
        recipe_id=recipe_id,
        user_id=user.id,
        dish_name=request.dish_name,
        recipe_text=request.recipe_text,
        analysis=request.analysis,
        tags=request.tags,
        notes=request.notes
    )
    
    return recipe_to_response(recipe)


@router.put("/saved/{recipe_id}", response_model=SavedRecipeResponse)
async def update_recipe(
    recipe_id: str,
    request: UpdateRecipeRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Update a saved recipe (favorite status, notes, tags)"""
    recipe = await crud.update_saved_recipe(
        session,
        recipe_id=recipe_id,
        user_id=user.id,
        is_favorite=request.is_favorite,
        notes=request.notes,
        tags=request.tags
    )
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    return recipe_to_response(recipe)


@router.delete("/saved/{recipe_id}")
async def delete_recipe(
    recipe_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Delete a saved recipe"""
    success = await crud.delete_saved_recipe(session, recipe_id, user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    return {"message": "Recipe deleted successfully"}

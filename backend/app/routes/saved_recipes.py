from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import uuid

from app.models.saved_recipe import (
    SaveRecipeRequest,
    UpdateRecipeRequest,
    SavedRecipeResponse,
    SavedRecipesListResponse
)
from app.database import (
    get_saved_recipes,
    get_saved_recipe_by_id,
    save_recipe,
    update_saved_recipe,
    delete_saved_recipe
)
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/saved", response_model=SavedRecipesListResponse)
async def list_saved_recipes(
    favorites_only: bool = False,
    user: User = Depends(get_current_user)
):
    """Get all saved recipes for the current user"""
    recipes = await get_saved_recipes(user.id, favorites_only=favorites_only)
    
    return SavedRecipesListResponse(
        recipes=[
            SavedRecipeResponse(
                id=r["id"],
                dish_name=r["dish_name"],
                recipe_text=r.get("recipe_text"),
                analysis=r.get("analysis"),
                is_favorite=bool(r.get("is_favorite", 0)),
                notes=r.get("notes"),
                tags=r.get("tags", []),
                created_at=r.get("created_at")
            )
            for r in recipes
        ],
        total=len(recipes)
    )


@router.get("/saved/{recipe_id}", response_model=SavedRecipeResponse)
async def get_recipe(
    recipe_id: str,
    user: User = Depends(get_current_user)
):
    """Get a single saved recipe by ID"""
    recipe = await get_saved_recipe_by_id(recipe_id, user.id)
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    return SavedRecipeResponse(
        id=recipe["id"],
        dish_name=recipe["dish_name"],
        recipe_text=recipe.get("recipe_text"),
        analysis=recipe.get("analysis"),
        is_favorite=bool(recipe.get("is_favorite", 0)),
        notes=recipe.get("notes"),
        tags=recipe.get("tags", []),
        created_at=recipe.get("created_at")
    )


@router.post("/saved", response_model=SavedRecipeResponse)
async def save_new_recipe(
    request: SaveRecipeRequest,
    user: User = Depends(get_current_user)
):
    """Save a new recipe after analysis"""
    recipe_id = str(uuid.uuid4())
    
    recipe = await save_recipe(
        recipe_id=recipe_id,
        user_id=user.id,
        dish_name=request.dish_name,
        recipe_text=request.recipe_text,
        analysis=request.analysis,
        tags=request.tags,
        notes=request.notes
    )
    
    return SavedRecipeResponse(
        id=recipe["id"],
        dish_name=recipe["dish_name"],
        recipe_text=recipe.get("recipe_text"),
        analysis=recipe.get("analysis"),
        is_favorite=bool(recipe.get("is_favorite", 0)),
        notes=recipe.get("notes"),
        tags=recipe.get("tags", []),
        created_at=recipe.get("created_at")
    )


@router.put("/saved/{recipe_id}", response_model=SavedRecipeResponse)
async def update_recipe(
    recipe_id: str,
    request: UpdateRecipeRequest,
    user: User = Depends(get_current_user)
):
    """Update a saved recipe (favorite status, notes, tags)"""
    recipe = await update_saved_recipe(
        recipe_id=recipe_id,
        user_id=user.id,
        is_favorite=request.is_favorite,
        notes=request.notes,
        tags=request.tags
    )
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    return SavedRecipeResponse(
        id=recipe["id"],
        dish_name=recipe["dish_name"],
        recipe_text=recipe.get("recipe_text"),
        analysis=recipe.get("analysis"),
        is_favorite=bool(recipe.get("is_favorite", 0)),
        notes=recipe.get("notes"),
        tags=recipe.get("tags", []),
        created_at=recipe.get("created_at")
    )


@router.delete("/saved/{recipe_id}")
async def delete_recipe(
    recipe_id: str,
    user: User = Depends(get_current_user)
):
    """Delete a saved recipe"""
    success = await delete_saved_recipe(recipe_id, user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    return {"message": "Recipe deleted successfully"}

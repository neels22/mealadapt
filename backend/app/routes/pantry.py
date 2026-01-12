from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from app import database as db
from app.services.ai_service import ai_service
from app.models.user import User
from app.middleware.auth import get_current_user

router = APIRouter()


class PantryItemCreate(BaseModel):
    name: str
    category: Optional[str] = None


class PantryItemResponse(BaseModel):
    id: int
    name: str
    category: Optional[str] = None


@router.get("/items", response_model=List[dict])
async def get_pantry_items(current_user: Optional[User] = Depends(get_current_user)):
    """Get all pantry items"""
    user_id = current_user.id if current_user else None
    return await db.get_pantry_items(user_id=user_id)


@router.post("/items", response_model=dict)
async def add_pantry_item(
    item: PantryItemCreate,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Add an item to the pantry"""
    user_id = current_user.id if current_user else None
    return await db.add_pantry_item(item.name, item.category, user_id=user_id)


@router.delete("/items/{item_id}")
async def delete_pantry_item(
    item_id: int,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Delete a pantry item"""
    user_id = current_user.id if current_user else None
    deleted = await db.delete_pantry_item(item_id, user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}


@router.delete("/items")
async def clear_pantry(current_user: Optional[User] = Depends(get_current_user)):
    """Clear all pantry items"""
    user_id = current_user.id if current_user else None
    await db.clear_pantry(user_id=user_id)
    return {"message": "Pantry cleared"}


@router.post("/suggest-recipes")
async def suggest_recipes(current_user: Optional[User] = Depends(get_current_user)):
    """Suggest recipes based on pantry ingredients and family profile"""
    user_id = current_user.id if current_user else None
    
    # Get pantry items
    items = await db.get_pantry_items(user_id=user_id)
    if not items:
        raise HTTPException(
            status_code=400,
            detail="Add some ingredients to your pantry first"
        )
    
    ingredients = [item["name"] for item in items]
    
    # Get family profile
    members = await db.get_all_members(user_id=user_id)
    family_profile = {"members": [m.model_dump() for m in members]}
    
    try:
        result = ai_service.suggest_recipes_from_ingredients(
            ingredients=ingredients,
            family_profile=family_profile
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

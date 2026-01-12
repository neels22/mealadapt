"""
Pantry management routes.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.services.ai_service import ai_service, AIBlocked, AIOutOfScope, AIInvalidOutput
from app.models.user import User
from app.models.family import FamilyMember, HealthCondition
from app.middleware.auth import get_current_user
from app.database import get_session
import json

router = APIRouter()


class PantryItemCreate(BaseModel):
    name: str
    category: Optional[str] = None


class PantryItemResponse(BaseModel):
    id: int
    name: str
    category: Optional[str] = None


def member_to_dict(member) -> dict:
    """Convert SQLModel FamilyMember to dict for AI service"""
    conditions = [
        {
            "type": cond.condition_type.value,
            "enabled": cond.enabled,
            "notes": cond.notes
        }
        for cond in member.conditions
    ]
    
    custom_restrictions = []
    if member.custom_restrictions:
        custom_restrictions = json.loads(member.custom_restrictions)
    
    preferences = None
    if member.preferences:
        preferences = json.loads(member.preferences)
    
    return {
        "id": member.id,
        "name": member.name,
        "avatar": member.avatar,
        "role": member.role.value,
        "conditions": conditions,
        "custom_restrictions": custom_restrictions,
        "preferences": preferences
    }


@router.get("/items", response_model=List[PantryItemResponse])
async def get_pantry_items(
    current_user: Optional[User] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get all pantry items"""
    user_id = current_user.id if current_user else None
    items = await crud.get_pantry_items(session, user_id=user_id)
    return [
        PantryItemResponse(id=item.id, name=item.name, category=item.category)
        for item in items
    ]


@router.post("/items", response_model=PantryItemResponse)
async def add_pantry_item(
    item: PantryItemCreate,
    current_user: Optional[User] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Add an item to the pantry"""
    user_id = current_user.id if current_user else None
    new_item = await crud.add_pantry_item(session, item.name, item.category, user_id=user_id)
    return PantryItemResponse(id=new_item.id, name=new_item.name, category=new_item.category)


@router.delete("/items/{item_id}")
async def delete_pantry_item(
    item_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Delete a pantry item"""
    user_id = current_user.id if current_user else None
    deleted = await crud.delete_pantry_item(session, item_id, user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}


@router.delete("/items")
async def clear_pantry(
    current_user: Optional[User] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Clear all pantry items"""
    user_id = current_user.id if current_user else None
    await crud.clear_pantry(session, user_id=user_id)
    return {"message": "Pantry cleared"}


@router.post("/suggest-recipes")
async def suggest_recipes(
    current_user: Optional[User] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Suggest recipes based on pantry ingredients and family profile"""
    user_id = current_user.id if current_user else None
    
    # Get pantry items
    items = await crud.get_pantry_items(session, user_id=user_id)
    if not items:
        raise HTTPException(
            status_code=400,
            detail="Add some ingredients to your pantry first"
        )
    
    ingredients = [item.name for item in items]
    
    # Get family profile
    members = await crud.get_all_members(session, user_id=user_id)
    family_profile = {"members": [member_to_dict(m) for m in members]}
    
    try:
        result = ai_service.suggest_recipes_from_ingredients(
            ingredients=ingredients,
            family_profile=family_profile
        )
        return result
    except AIOutOfScope as e:
        raise HTTPException(status_code=400, detail={"error": "out_of_scope", "message": str(e)})
    except AIBlocked as e:
        raise HTTPException(status_code=422, detail={"error": "blocked", "message": str(e)})
    except AIInvalidOutput as e:
        raise HTTPException(status_code=502, detail={"error": "invalid_model_output", "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""
Shopping list management routes.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.shopping import (
    ShoppingItem,
    CreateShoppingListRequest,
    GenerateShoppingListRequest,
    AddItemRequest,
    UpdateItemRequest,
    ShoppingListResponse,
    ShoppingListsResponse
)
from app import crud
from app.services.ai_service import ai_service, AIBlocked, AIOutOfScope, AIInvalidOutput
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import check_ai_rate_limit
from app.models.user import User
from app.database import get_session

router = APIRouter()


def list_to_response(shopping_list) -> ShoppingListResponse:
    """Convert SQLModel ShoppingList to Pydantic response"""
    items = [
        ShoppingItem(
            id=item.id,
            ingredient=item.ingredient,
            quantity=item.quantity,
            category=item.category,
            is_checked=item.is_checked,
            source_recipe_id=item.source_recipe_id
        )
        for item in (shopping_list.items or [])
    ]
    
    return ShoppingListResponse(
        id=shopping_list.id,
        name=shopping_list.name,
        items=items,
        created_at=str(shopping_list.created_at) if shopping_list.created_at else None,
        completed_at=str(shopping_list.completed_at) if shopping_list.completed_at else None
    )


@router.get("/lists", response_model=ShoppingListsResponse)
async def list_shopping_lists(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get all shopping lists for the current user"""
    lists = await crud.get_shopping_lists(session, user.id)
    
    return ShoppingListsResponse(
        lists=[list_to_response(lst) for lst in lists],
        total=len(lists)
    )


@router.get("/lists/{list_id}", response_model=ShoppingListResponse)
async def get_list(
    list_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get a single shopping list by ID"""
    shopping_list = await crud.get_shopping_list_by_id(session, list_id, user.id)
    
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    
    return list_to_response(shopping_list)


@router.post("/lists", response_model=ShoppingListResponse)
async def create_list(
    request: CreateShoppingListRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Create a new shopping list"""
    list_id = str(uuid.uuid4())
    
    items = [
        {
            "ingredient": item.ingredient,
            "quantity": item.quantity,
            "category": item.category,
            "source_recipe_id": item.source_recipe_id
        }
        for item in request.items
    ]
    
    shopping_list = await crud.create_shopping_list(
        session,
        list_id=list_id,
        user_id=user.id,
        name=request.name,
        items=items
    )
    
    return list_to_response(shopping_list)


@router.post("/lists/generate", response_model=ShoppingListResponse)
async def generate_list_from_recipes(
    request: GenerateShoppingListRequest,
    user: User = Depends(check_ai_rate_limit("extract_ingredients_from_recipes")),
    session: AsyncSession = Depends(get_session)
):
    """Generate a shopping list from saved recipes using AI"""
    # Fetch all recipes
    recipes = []
    for recipe_id in request.recipe_ids:
        recipe = await crud.get_saved_recipe_by_id(session, recipe_id, user.id)
        if recipe:
            recipes.append({
                "id": recipe.id,
                "dish_name": recipe.dish_name,
                "recipe_text": recipe.recipe_text or ""
            })
    
    if not recipes:
        raise HTTPException(status_code=400, detail="No valid recipes found")
    
    try:
        # Use AI to extract ingredients
        extracted_ingredients = ai_service.extract_ingredients_from_recipes(recipes)
        
        # Create shopping list
        list_id = str(uuid.uuid4())
        items = [
            {
                "ingredient": ing["ingredient"],
                "quantity": ing.get("quantity"),
                "category": ing.get("category"),
                "source_recipe_id": None  # Could track which recipe each ingredient came from
            }
            for ing in extracted_ingredients
        ]
        
        shopping_list = await crud.create_shopping_list(
            session,
            list_id=list_id,
            user_id=user.id,
            name=request.name,
            items=items
        )
        
        return list_to_response(shopping_list)
    except AIOutOfScope as e:
        raise HTTPException(status_code=400, detail={"error": "out_of_scope", "message": str(e)})
    except AIBlocked as e:
        raise HTTPException(status_code=422, detail={"error": "blocked", "message": str(e)})
    except AIInvalidOutput as e:
        raise HTTPException(status_code=502, detail={"error": "invalid_model_output", "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate shopping list: {str(e)}")


@router.post("/lists/{list_id}/items", response_model=ShoppingItem)
async def add_item(
    list_id: str,
    request: AddItemRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Add an item to a shopping list"""
    item = await crud.add_shopping_item(
        session,
        list_id=list_id,
        user_id=user.id,
        ingredient=request.ingredient,
        quantity=request.quantity,
        category=request.category
    )
    
    if not item:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    
    return ShoppingItem(
        id=item.id,
        ingredient=item.ingredient,
        quantity=item.quantity,
        category=item.category,
        is_checked=item.is_checked
    )


@router.put("/items/{item_id}", response_model=ShoppingItem)
async def update_item(
    item_id: int,
    request: UpdateItemRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Update a shopping item (toggle checked, update quantity)"""
    item = await crud.update_shopping_item(
        session,
        item_id=item_id,
        user_id=user.id,
        is_checked=request.is_checked,
        quantity=request.quantity
    )
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return ShoppingItem(
        id=item.id,
        ingredient=item.ingredient,
        quantity=item.quantity,
        category=item.category,
        is_checked=item.is_checked
    )


@router.delete("/items/{item_id}")
async def remove_item(
    item_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Delete a shopping item"""
    success = await crud.delete_shopping_item(session, item_id, user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"message": "Item deleted successfully"}


@router.delete("/lists/{list_id}")
async def remove_list(
    list_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Delete a shopping list"""
    success = await crud.delete_shopping_list(session, list_id, user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    
    return {"message": "Shopping list deleted successfully"}


@router.post("/lists/{list_id}/complete", response_model=ShoppingListResponse)
async def mark_complete(
    list_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Mark a shopping list as completed"""
    shopping_list = await crud.complete_shopping_list(session, list_id, user.id)
    
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    
    return list_to_response(shopping_list)

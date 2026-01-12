from fastapi import APIRouter, HTTPException, Depends
from typing import List
import uuid

from app.models.shopping import (
    ShoppingItem,
    CreateShoppingListRequest,
    GenerateShoppingListRequest,
    AddItemRequest,
    UpdateItemRequest,
    ShoppingListResponse,
    ShoppingListsResponse
)
from app.database import (
    get_shopping_lists,
    get_shopping_list_by_id,
    create_shopping_list,
    add_shopping_item,
    update_shopping_item,
    delete_shopping_item,
    delete_shopping_list,
    complete_shopping_list,
    get_saved_recipe_by_id
)
from app.services.ai_service import ai_service
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter()


def format_list_response(shopping_list: dict) -> ShoppingListResponse:
    """Format a shopping list dict to response model"""
    return ShoppingListResponse(
        id=shopping_list["id"],
        name=shopping_list["name"],
        items=[
            ShoppingItem(
                id=item.get("id"),
                ingredient=item["ingredient"],
                quantity=item.get("quantity"),
                category=item.get("category"),
                is_checked=bool(item.get("is_checked", 0)),
                source_recipe_id=item.get("source_recipe_id")
            )
            for item in shopping_list.get("items", [])
        ],
        created_at=shopping_list.get("created_at"),
        completed_at=shopping_list.get("completed_at")
    )


@router.get("/lists", response_model=ShoppingListsResponse)
async def list_shopping_lists(user: User = Depends(get_current_user)):
    """Get all shopping lists for the current user"""
    lists = await get_shopping_lists(user.id)
    
    return ShoppingListsResponse(
        lists=[format_list_response(lst) for lst in lists],
        total=len(lists)
    )


@router.get("/lists/{list_id}", response_model=ShoppingListResponse)
async def get_list(list_id: str, user: User = Depends(get_current_user)):
    """Get a single shopping list by ID"""
    shopping_list = await get_shopping_list_by_id(list_id, user.id)
    
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    
    return format_list_response(shopping_list)


@router.post("/lists", response_model=ShoppingListResponse)
async def create_list(
    request: CreateShoppingListRequest,
    user: User = Depends(get_current_user)
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
    
    shopping_list = await create_shopping_list(
        list_id=list_id,
        user_id=user.id,
        name=request.name,
        items=items
    )
    
    return format_list_response(shopping_list)


@router.post("/lists/generate", response_model=ShoppingListResponse)
async def generate_list_from_recipes(
    request: GenerateShoppingListRequest,
    user: User = Depends(get_current_user)
):
    """Generate a shopping list from saved recipes using AI"""
    # Fetch all recipes
    recipes = []
    for recipe_id in request.recipe_ids:
        recipe = await get_saved_recipe_by_id(recipe_id, user.id)
        if recipe:
            recipes.append({
                "id": recipe["id"],
                "dish_name": recipe["dish_name"],
                "recipe_text": recipe.get("recipe_text", "")
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
        
        shopping_list = await create_shopping_list(
            list_id=list_id,
            user_id=user.id,
            name=request.name,
            items=items
        )
        
        return format_list_response(shopping_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate shopping list: {str(e)}")


@router.post("/lists/{list_id}/items", response_model=ShoppingItem)
async def add_item(
    list_id: str,
    request: AddItemRequest,
    user: User = Depends(get_current_user)
):
    """Add an item to a shopping list"""
    item = await add_shopping_item(
        list_id=list_id,
        user_id=user.id,
        ingredient=request.ingredient,
        quantity=request.quantity,
        category=request.category
    )
    
    if not item:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    
    return ShoppingItem(
        id=item["id"],
        ingredient=item["ingredient"],
        quantity=item.get("quantity"),
        category=item.get("category"),
        is_checked=bool(item.get("is_checked", 0))
    )


@router.put("/items/{item_id}", response_model=ShoppingItem)
async def update_item(
    item_id: int,
    request: UpdateItemRequest,
    user: User = Depends(get_current_user)
):
    """Update a shopping item (toggle checked, update quantity)"""
    item = await update_shopping_item(
        item_id=item_id,
        user_id=user.id,
        is_checked=request.is_checked,
        quantity=request.quantity
    )
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return ShoppingItem(
        id=item["id"],
        ingredient=item["ingredient"],
        quantity=item.get("quantity"),
        category=item.get("category"),
        is_checked=bool(item.get("is_checked", 0))
    )


@router.delete("/items/{item_id}")
async def remove_item(item_id: int, user: User = Depends(get_current_user)):
    """Delete a shopping item"""
    success = await delete_shopping_item(item_id, user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"message": "Item deleted successfully"}


@router.delete("/lists/{list_id}")
async def remove_list(list_id: str, user: User = Depends(get_current_user)):
    """Delete a shopping list"""
    success = await delete_shopping_list(list_id, user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    
    return {"message": "Shopping list deleted successfully"}


@router.post("/lists/{list_id}/complete", response_model=ShoppingListResponse)
async def mark_complete(list_id: str, user: User = Depends(get_current_user)):
    """Mark a shopping list as completed"""
    shopping_list = await complete_shopping_list(list_id, user.id)
    
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    
    return format_list_response(shopping_list)

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid


class ShoppingItem(BaseModel):
    """An item in a shopping list"""
    id: Optional[int] = None
    ingredient: str
    quantity: Optional[str] = None
    category: Optional[str] = None  # produce, dairy, meat, pantry, etc.
    is_checked: bool = False
    source_recipe_id: Optional[str] = None


class CreateShoppingListRequest(BaseModel):
    """Request to create a new shopping list"""
    name: str
    items: List[ShoppingItem] = []


class GenerateShoppingListRequest(BaseModel):
    """Request to generate a shopping list from saved recipes"""
    name: str
    recipe_ids: List[str]


class AddItemRequest(BaseModel):
    """Request to add an item to a shopping list"""
    ingredient: str
    quantity: Optional[str] = None
    category: Optional[str] = None


class UpdateItemRequest(BaseModel):
    """Request to update a shopping item"""
    is_checked: Optional[bool] = None
    quantity: Optional[str] = None


class ShoppingList(BaseModel):
    """A shopping list with items"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    items: List[ShoppingItem] = []
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ShoppingListResponse(BaseModel):
    """Response containing a shopping list"""
    id: str
    name: str
    items: List[ShoppingItem] = []
    created_at: Optional[str] = None
    completed_at: Optional[str] = None


class ShoppingListsResponse(BaseModel):
    """Response containing list of shopping lists"""
    lists: List[ShoppingListResponse]
    total: int


class ExtractedIngredient(BaseModel):
    """An ingredient extracted from a recipe"""
    ingredient: str
    quantity: str
    category: str

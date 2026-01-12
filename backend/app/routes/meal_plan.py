from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from datetime import datetime, timedelta
import uuid

from app.models.meal_plan import (
    PlannedMeal,
    AddMealRequest,
    UpdateMealRequest,
    MealPlanResponse,
    GenerateShoppingFromPlanRequest
)
from app.models.shopping import ShoppingListResponse, ShoppingItem
from app.database import (
    get_or_create_meal_plan,
    add_planned_meal,
    update_planned_meal,
    delete_planned_meal,
    get_week_recipes,
    create_shopping_list
)
from app.services.ai_service import ai_service
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter()


def get_monday(date_str: str = None) -> str:
    """Get the Monday of the week for a given date"""
    if date_str:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    else:
        dt = datetime.now()
    
    # Get Monday (weekday 0)
    monday = dt - timedelta(days=dt.weekday())
    return monday.strftime("%Y-%m-%d")


def format_meal(meal: dict) -> PlannedMeal:
    """Format a meal dict to PlannedMeal model"""
    return PlannedMeal(
        id=meal.get("id"),
        plan_id=meal.get("plan_id"),
        recipe_id=meal.get("recipe_id"),
        date=meal.get("date"),
        meal_type=meal.get("meal_type"),
        servings=meal.get("servings", 1),
        notes=meal.get("notes"),
        dish_name=meal.get("dish_name"),
        analysis=meal.get("analysis")
    )


@router.get("", response_model=MealPlanResponse)
async def get_meal_plan(
    week: Optional[str] = Query(None, description="Date in YYYY-MM-DD format, will get the week containing this date"),
    user: User = Depends(get_current_user)
):
    """Get meal plan for a week"""
    week_start = get_monday(week)
    
    plan = await get_or_create_meal_plan(user.id, week_start)
    
    return MealPlanResponse(
        id=plan["id"],
        week_start=plan["week_start"],
        meals=[format_meal(m) for m in plan.get("meals", [])],
        created_at=plan.get("created_at")
    )


@router.post("/meals", response_model=PlannedMeal)
async def add_meal(
    request: AddMealRequest,
    user: User = Depends(get_current_user)
):
    """Add a meal to the plan"""
    # Get the week start from the date
    week_start = get_monday(request.date)
    
    # Get or create the plan for this week
    plan = await get_or_create_meal_plan(user.id, week_start)
    
    meal = await add_planned_meal(
        plan_id=plan["id"],
        user_id=user.id,
        recipe_id=request.recipe_id,
        date=request.date,
        meal_type=request.meal_type.value,
        servings=request.servings,
        notes=request.notes
    )
    
    if not meal:
        raise HTTPException(status_code=400, detail="Failed to add meal")
    
    return format_meal(meal)


@router.put("/meals/{meal_id}", response_model=PlannedMeal)
async def update_meal(
    meal_id: int,
    request: UpdateMealRequest,
    user: User = Depends(get_current_user)
):
    """Update a planned meal"""
    meal = await update_planned_meal(
        meal_id=meal_id,
        user_id=user.id,
        recipe_id=request.recipe_id,
        date=request.date,
        meal_type=request.meal_type.value if request.meal_type else None,
        servings=request.servings,
        notes=request.notes
    )
    
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    return format_meal(meal)


@router.delete("/meals/{meal_id}")
async def remove_meal(
    meal_id: int,
    user: User = Depends(get_current_user)
):
    """Remove a meal from the plan"""
    success = await delete_planned_meal(meal_id, user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    return {"message": "Meal removed from plan"}


@router.post("/{plan_id}/generate-shopping", response_model=ShoppingListResponse)
async def generate_shopping_from_plan(
    plan_id: str,
    request: GenerateShoppingFromPlanRequest,
    user: User = Depends(get_current_user)
):
    """Generate a shopping list from all recipes in the meal plan"""
    # Get all recipes from the plan
    recipes = await get_week_recipes(plan_id, user.id)
    
    if not recipes:
        raise HTTPException(status_code=400, detail="No recipes in this meal plan")
    
    try:
        # Use AI to extract and combine ingredients
        extracted_ingredients = ai_service.extract_ingredients_from_recipes([
            {"dish_name": r["dish_name"], "recipe_text": r.get("recipe_text", "")}
            for r in recipes
        ])
        
        # Create shopping list
        list_id = str(uuid.uuid4())
        items = [
            {
                "ingredient": ing["ingredient"],
                "quantity": ing.get("quantity"),
                "category": ing.get("category"),
                "source_recipe_id": None
            }
            for ing in extracted_ingredients
        ]
        
        shopping_list = await create_shopping_list(
            list_id=list_id,
            user_id=user.id,
            name=request.list_name,
            items=items
        )
        
        return ShoppingListResponse(
            id=shopping_list["id"],
            name=shopping_list["name"],
            items=[
                ShoppingItem(
                    id=item.get("id"),
                    ingredient=item["ingredient"],
                    quantity=item.get("quantity"),
                    category=item.get("category"),
                    is_checked=bool(item.get("is_checked", 0))
                )
                for item in shopping_list.get("items", [])
            ],
            created_at=shopping_list.get("created_at")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate shopping list: {str(e)}")

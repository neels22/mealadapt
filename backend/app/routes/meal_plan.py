"""
Meal planning routes.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from datetime import datetime, timedelta
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meal_plan import (
    PlannedMeal,
    AddMealRequest,
    UpdateMealRequest,
    MealPlanResponse,
    GenerateShoppingFromPlanRequest
)
from app.models.shopping import ShoppingListResponse, ShoppingItem
from app import crud
from app.services.ai_service import ai_service, AIBlocked, AIOutOfScope, AIInvalidOutput
from app.middleware.auth import get_current_user
from app.models.user import User
from app.database import get_session

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


def meal_to_response(meal) -> PlannedMeal:
    """Convert SQLModel PlannedMeal to Pydantic response"""
    dish_name = None
    analysis = None
    
    if meal.recipe:
        dish_name = meal.recipe.dish_name
        analysis = meal.recipe.get_analysis()
    
    return PlannedMeal(
        id=meal.id,
        plan_id=meal.plan_id,
        recipe_id=meal.recipe_id,
        date=meal.date,
        meal_type=meal.meal_type,
        servings=meal.servings,
        notes=meal.notes,
        dish_name=dish_name,
        analysis=analysis
    )


@router.get("", response_model=MealPlanResponse)
async def get_meal_plan(
    week: Optional[str] = Query(None, description="Date in YYYY-MM-DD format, will get the week containing this date"),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get meal plan for a week"""
    week_start = get_monday(week)
    
    plan = await crud.get_or_create_meal_plan(session, user.id, week_start)
    
    meals = [meal_to_response(m) for m in (plan.meals or [])]
    
    return MealPlanResponse(
        id=plan.id,
        week_start=plan.week_start,
        meals=meals,
        created_at=str(plan.created_at) if plan.created_at else None
    )


@router.post("/meals", response_model=PlannedMeal)
async def add_meal(
    request: AddMealRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Add a meal to the plan"""
    # Get the week start from the date
    week_start = get_monday(request.date)
    
    # Get or create the plan for this week
    plan = await crud.get_or_create_meal_plan(session, user.id, week_start)
    
    meal = await crud.add_planned_meal(
        session,
        plan_id=plan.id,
        user_id=user.id,
        recipe_id=request.recipe_id,
        date=request.date,
        meal_type=request.meal_type.value,
        servings=request.servings,
        notes=request.notes
    )
    
    if not meal:
        raise HTTPException(status_code=400, detail="Failed to add meal")
    
    return meal_to_response(meal)


@router.put("/meals/{meal_id}", response_model=PlannedMeal)
async def update_meal(
    meal_id: int,
    request: UpdateMealRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Update a planned meal"""
    meal = await crud.update_planned_meal(
        session,
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
    
    return meal_to_response(meal)


@router.delete("/meals/{meal_id}")
async def remove_meal(
    meal_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Remove a meal from the plan"""
    success = await crud.delete_planned_meal(session, meal_id, user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    return {"message": "Meal removed from plan"}


@router.post("/{plan_id}/generate-shopping", response_model=ShoppingListResponse)
async def generate_shopping_from_plan(
    plan_id: str,
    request: GenerateShoppingFromPlanRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Generate a shopping list from all recipes in the meal plan"""
    # Get all recipes from the plan
    recipes = await crud.get_week_recipes(session, plan_id, user.id)
    
    if not recipes:
        raise HTTPException(status_code=400, detail="No recipes in this meal plan")
    
    try:
        # Use AI to extract and combine ingredients
        extracted_ingredients = ai_service.extract_ingredients_from_recipes([
            {"dish_name": r.dish_name, "recipe_text": r.recipe_text or ""}
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
        
        shopping_list = await crud.create_shopping_list(
            session,
            list_id=list_id,
            user_id=user.id,
            name=request.list_name,
            items=items
        )
        
        return ShoppingListResponse(
            id=shopping_list.id,
            name=shopping_list.name,
            items=[
                ShoppingItem(
                    id=item.id,
                    ingredient=item.ingredient,
                    quantity=item.quantity,
                    category=item.category,
                    is_checked=item.is_checked
                )
                for item in (shopping_list.items or [])
            ],
            created_at=str(shopping_list.created_at) if shopping_list.created_at else None
        )
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

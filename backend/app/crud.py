"""
CRUD operations for all database models using SQLModel.
All functions accept an AsyncSession as the first parameter.
"""
import json
from datetime import datetime, date
from typing import List, Optional
from uuid import uuid4
from sqlmodel import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.tables import (
    User, FamilyMember, HealthCondition, PantryItem,
    SavedRecipe, RecipeTag, ShoppingList, ShoppingItem,
    MealPlan, PlannedMeal, BarcodeCache, RefreshToken, BlacklistedToken,
    LLMUsage,
    Role, ConditionType
)


# ============== User CRUD ==============

async def create_user(
    session: AsyncSession,
    user_id: str,
    email: str,
    password_hash: str,
    name: str
) -> User:
    """Create a new user"""
    user = User(
        id=user_id,
        email=email,
        password_hash=password_hash,
        name=name
    )
    session.add(user)
    await session.flush()
    return user


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    """Get user by email"""
    statement = select(User).where(User.email == email)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: str) -> Optional[User]:
    """Get user by ID"""
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def update_user(
    session: AsyncSession,
    user_id: str,
    name: Optional[str] = None,
    email: Optional[str] = None,
    password_hash: Optional[str] = None
) -> Optional[User]:
    """Update user details"""
    user = await get_user_by_id(session, user_id)
    if not user:
        return None
    
    if name is not None:
        user.name = name
    if email is not None:
        user.email = email
    if password_hash is not None:
        user.password_hash = password_hash
    user.updated_at = datetime.utcnow()
    
    await session.flush()
    return user


async def delete_user(session: AsyncSession, user_id: str) -> bool:
    """Delete a user and all their data (cascades via relationships)"""
    user = await get_user_by_id(session, user_id)
    if not user:
        return False
    
    # Delete related data that might not have cascade
    await session.execute(delete(PantryItem).where(PantryItem.user_id == user_id))
    await session.execute(delete(RefreshToken).where(RefreshToken.user_id == user_id))
    
    # Delete shopping items and lists
    shopping_lists = await session.execute(
        select(ShoppingList).where(ShoppingList.user_id == user_id)
    )
    for sl in shopping_lists.scalars():
        await session.execute(delete(ShoppingItem).where(ShoppingItem.list_id == sl.id))
    await session.execute(delete(ShoppingList).where(ShoppingList.user_id == user_id))
    
    # Delete meal plans and planned meals
    meal_plans = await session.execute(
        select(MealPlan).where(MealPlan.user_id == user_id)
    )
    for mp in meal_plans.scalars():
        await session.execute(delete(PlannedMeal).where(PlannedMeal.plan_id == mp.id))
    await session.execute(delete(MealPlan).where(MealPlan.user_id == user_id))
    
    # Delete recipes and tags
    recipes = await session.execute(
        select(SavedRecipe).where(SavedRecipe.user_id == user_id)
    )
    for r in recipes.scalars():
        await session.execute(delete(RecipeTag).where(RecipeTag.recipe_id == r.id))
    await session.execute(delete(SavedRecipe).where(SavedRecipe.user_id == user_id))
    
    # Delete family members and conditions
    members = await session.execute(
        select(FamilyMember).where(FamilyMember.user_id == user_id)
    )
    for m in members.scalars():
        await session.execute(delete(HealthCondition).where(HealthCondition.member_id == m.id))
    await session.execute(delete(FamilyMember).where(FamilyMember.user_id == user_id))
    
    # Delete user
    await session.delete(user)
    await session.flush()
    return True


# ============== Family Member CRUD ==============

async def get_all_members(
    session: AsyncSession,
    user_id: Optional[str] = None
) -> List[FamilyMember]:
    """Get all family members with their conditions"""
    if user_id:
        statement = select(FamilyMember).where(
            FamilyMember.user_id == user_id
        ).options(selectinload(FamilyMember.conditions))
    else:
        statement = select(FamilyMember).where(
            FamilyMember.user_id == None
        ).options(selectinload(FamilyMember.conditions))
    
    result = await session.execute(statement)
    return list(result.scalars().all())


async def get_member_by_id(
    session: AsyncSession,
    member_id: str
) -> Optional[FamilyMember]:
    """Get a single family member by ID"""
    statement = select(FamilyMember).where(
        FamilyMember.id == member_id
    ).options(selectinload(FamilyMember.conditions))
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def add_member(
    session: AsyncSession,
    member_id: str,
    name: str,
    avatar: str,
    role: Role,
    conditions: List[dict],
    custom_restrictions: List[str],
    preferences: Optional[dict],
    user_id: Optional[str] = None
) -> FamilyMember:
    """Add a new family member"""
    member = FamilyMember(
        id=member_id,
        user_id=user_id,
        name=name,
        avatar=avatar,
        role=role,
        custom_restrictions=json.dumps(custom_restrictions),
        preferences=json.dumps(preferences) if preferences else None
    )
    session.add(member)
    await session.flush()
    
    # Add conditions
    for cond in conditions:
        condition = HealthCondition(
            member_id=member.id,
            condition_type=cond["type"],
            enabled=cond.get("enabled", False),
            notes=cond.get("notes")
        )
        session.add(condition)
    
    await session.flush()
    
    # Reload with conditions
    return await get_member_by_id(session, member.id)


async def update_member(
    session: AsyncSession,
    member_id: str,
    name: str,
    avatar: str,
    role: Role,
    conditions: List[dict],
    custom_restrictions: List[str],
    preferences: Optional[dict]
) -> Optional[FamilyMember]:
    """Update an existing family member"""
    member = await get_member_by_id(session, member_id)
    if not member:
        return None
    
    member.name = name
    member.avatar = avatar
    member.role = role
    member.custom_restrictions = json.dumps(custom_restrictions)
    member.preferences = json.dumps(preferences) if preferences else None
    
    # Delete old conditions and add new ones
    await session.execute(
        delete(HealthCondition).where(HealthCondition.member_id == member_id)
    )
    
    for cond in conditions:
        condition = HealthCondition(
            member_id=member_id,
            condition_type=cond["type"],
            enabled=cond.get("enabled", False),
            notes=cond.get("notes")
        )
        session.add(condition)
    
    await session.flush()
    return await get_member_by_id(session, member_id)


async def delete_member(session: AsyncSession, member_id: str) -> bool:
    """Delete a family member"""
    member = await get_member_by_id(session, member_id)
    if not member:
        return False
    
    await session.execute(
        delete(HealthCondition).where(HealthCondition.member_id == member_id)
    )
    await session.delete(member)
    await session.flush()
    return True


# ============== Pantry CRUD ==============

async def get_pantry_items(
    session: AsyncSession,
    user_id: Optional[str] = None
) -> List[PantryItem]:
    """Get all pantry items"""
    if user_id:
        statement = select(PantryItem).where(
            PantryItem.user_id == user_id
        ).order_by(PantryItem.added_at.desc())
    else:
        statement = select(PantryItem).where(
            PantryItem.user_id == None
        ).order_by(PantryItem.added_at.desc())
    
    result = await session.execute(statement)
    return list(result.scalars().all())


async def add_pantry_item(
    session: AsyncSession,
    name: str,
    category: Optional[str] = None,
    user_id: Optional[str] = None
) -> PantryItem:
    """Add an item to the pantry"""
    item = PantryItem(
        name=name,
        category=category,
        user_id=user_id
    )
    session.add(item)
    await session.flush()
    return item


async def delete_pantry_item(
    session: AsyncSession,
    item_id: int,
    user_id: Optional[str] = None
) -> bool:
    """Delete a pantry item"""
    if user_id:
        statement = select(PantryItem).where(
            PantryItem.id == item_id,
            PantryItem.user_id == user_id
        )
    else:
        statement = select(PantryItem).where(
            PantryItem.id == item_id,
            PantryItem.user_id == None
        )
    
    result = await session.execute(statement)
    item = result.scalar_one_or_none()
    
    if not item:
        return False
    
    await session.delete(item)
    await session.flush()
    return True


async def clear_pantry(
    session: AsyncSession,
    user_id: Optional[str] = None
) -> None:
    """Clear all pantry items for a user"""
    if user_id:
        await session.execute(
            delete(PantryItem).where(PantryItem.user_id == user_id)
        )
    else:
        await session.execute(
            delete(PantryItem).where(PantryItem.user_id == None)
        )
    await session.flush()


# ============== Saved Recipe CRUD ==============

async def get_saved_recipes(
    session: AsyncSession,
    user_id: str,
    favorites_only: bool = False
) -> List[SavedRecipe]:
    """Get all saved recipes for a user"""
    statement = select(SavedRecipe).where(
        SavedRecipe.user_id == user_id
    ).options(selectinload(SavedRecipe.tags))
    
    if favorites_only:
        statement = statement.where(SavedRecipe.is_favorite == True)
    
    statement = statement.order_by(SavedRecipe.created_at.desc())
    
    result = await session.execute(statement)
    return list(result.scalars().all())


async def get_saved_recipe_by_id(
    session: AsyncSession,
    recipe_id: str,
    user_id: str
) -> Optional[SavedRecipe]:
    """Get a single saved recipe by ID"""
    statement = select(SavedRecipe).where(
        SavedRecipe.id == recipe_id,
        SavedRecipe.user_id == user_id
    ).options(selectinload(SavedRecipe.tags))
    
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def save_recipe(
    session: AsyncSession,
    recipe_id: str,
    user_id: str,
    dish_name: str,
    recipe_text: str,
    analysis: dict,
    tags: List[str] = None,
    notes: str = None
) -> SavedRecipe:
    """Save a new recipe"""
    recipe = SavedRecipe(
        id=recipe_id,
        user_id=user_id,
        dish_name=dish_name,
        recipe_text=recipe_text,
        analysis_json=json.dumps(analysis),
        notes=notes
    )
    session.add(recipe)
    await session.flush()
    
    # Add tags
    if tags:
        for tag in tags:
            tag_obj = RecipeTag(recipe_id=recipe_id, tag=tag)
            session.add(tag_obj)
    
    await session.flush()
    return await get_saved_recipe_by_id(session, recipe_id, user_id)


async def update_saved_recipe(
    session: AsyncSession,
    recipe_id: str,
    user_id: str,
    is_favorite: Optional[bool] = None,
    notes: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Optional[SavedRecipe]:
    """Update a saved recipe"""
    recipe = await get_saved_recipe_by_id(session, recipe_id, user_id)
    if not recipe:
        return None
    
    if is_favorite is not None:
        recipe.is_favorite = is_favorite
    if notes is not None:
        recipe.notes = notes
    
    # Update tags if provided
    if tags is not None:
        await session.execute(
            delete(RecipeTag).where(RecipeTag.recipe_id == recipe_id)
        )
        for tag in tags:
            tag_obj = RecipeTag(recipe_id=recipe_id, tag=tag)
            session.add(tag_obj)
    
    await session.flush()
    return await get_saved_recipe_by_id(session, recipe_id, user_id)


async def delete_saved_recipe(
    session: AsyncSession,
    recipe_id: str,
    user_id: str
) -> bool:
    """Delete a saved recipe"""
    recipe = await get_saved_recipe_by_id(session, recipe_id, user_id)
    if not recipe:
        return False
    
    await session.execute(
        delete(RecipeTag).where(RecipeTag.recipe_id == recipe_id)
    )
    await session.delete(recipe)
    await session.flush()
    return True


# ============== Shopping List CRUD ==============

async def get_shopping_lists(
    session: AsyncSession,
    user_id: str
) -> List[ShoppingList]:
    """Get all shopping lists for a user"""
    statement = select(ShoppingList).where(
        ShoppingList.user_id == user_id
    ).options(selectinload(ShoppingList.items)).order_by(ShoppingList.created_at.desc())
    
    result = await session.execute(statement)
    return list(result.scalars().all())


async def get_shopping_list_by_id(
    session: AsyncSession,
    list_id: str,
    user_id: str
) -> Optional[ShoppingList]:
    """Get a single shopping list by ID"""
    statement = select(ShoppingList).where(
        ShoppingList.id == list_id,
        ShoppingList.user_id == user_id
    ).options(selectinload(ShoppingList.items))
    
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def create_shopping_list(
    session: AsyncSession,
    list_id: str,
    user_id: str,
    name: str,
    items: List[dict] = None
) -> ShoppingList:
    """Create a new shopping list"""
    shopping_list = ShoppingList(
        id=list_id,
        user_id=user_id,
        name=name
    )
    session.add(shopping_list)
    await session.flush()
    
    # Add items if provided
    if items:
        for item in items:
            item_obj = ShoppingItem(
                list_id=list_id,
                ingredient=item["ingredient"],
                quantity=item.get("quantity"),
                category=item.get("category"),
                source_recipe_id=item.get("source_recipe_id")
            )
            session.add(item_obj)
    
    await session.flush()
    return await get_shopping_list_by_id(session, list_id, user_id)


async def add_shopping_item(
    session: AsyncSession,
    list_id: str,
    user_id: str,
    ingredient: str,
    quantity: Optional[str] = None,
    category: Optional[str] = None
) -> Optional[ShoppingItem]:
    """Add an item to a shopping list"""
    # Verify list belongs to user
    shopping_list = await get_shopping_list_by_id(session, list_id, user_id)
    if not shopping_list:
        return None
    
    item = ShoppingItem(
        list_id=list_id,
        ingredient=ingredient,
        quantity=quantity,
        category=category
    )
    session.add(item)
    await session.flush()
    return item


async def update_shopping_item(
    session: AsyncSession,
    item_id: int,
    user_id: str,
    is_checked: Optional[bool] = None,
    quantity: Optional[str] = None
) -> Optional[ShoppingItem]:
    """Update a shopping item"""
    # Get item and verify ownership
    statement = select(ShoppingItem).join(ShoppingList).where(
        ShoppingItem.id == item_id,
        ShoppingList.user_id == user_id
    )
    result = await session.execute(statement)
    item = result.scalar_one_or_none()
    
    if not item:
        return None
    
    if is_checked is not None:
        item.is_checked = is_checked
    if quantity is not None:
        item.quantity = quantity
    
    await session.flush()
    return item


async def delete_shopping_item(
    session: AsyncSession,
    item_id: int,
    user_id: str
) -> bool:
    """Delete a shopping item"""
    statement = select(ShoppingItem).join(ShoppingList).where(
        ShoppingItem.id == item_id,
        ShoppingList.user_id == user_id
    )
    result = await session.execute(statement)
    item = result.scalar_one_or_none()
    
    if not item:
        return False
    
    await session.delete(item)
    await session.flush()
    return True


async def delete_shopping_list(
    session: AsyncSession,
    list_id: str,
    user_id: str
) -> bool:
    """Delete a shopping list and all its items"""
    shopping_list = await get_shopping_list_by_id(session, list_id, user_id)
    if not shopping_list:
        return False
    
    await session.execute(
        delete(ShoppingItem).where(ShoppingItem.list_id == list_id)
    )
    await session.delete(shopping_list)
    await session.flush()
    return True


async def complete_shopping_list(
    session: AsyncSession,
    list_id: str,
    user_id: str
) -> Optional[ShoppingList]:
    """Mark a shopping list as completed"""
    shopping_list = await get_shopping_list_by_id(session, list_id, user_id)
    if not shopping_list:
        return None
    
    shopping_list.completed_at = datetime.utcnow()
    await session.flush()
    return shopping_list


# ============== Meal Plan CRUD ==============

async def get_or_create_meal_plan(
    session: AsyncSession,
    user_id: str,
    week_start: str,
    plan_id: str = None
) -> MealPlan:
    """Get meal plan for a week, creating if it doesn't exist"""
    statement = select(MealPlan).where(
        MealPlan.user_id == user_id,
        MealPlan.week_start == week_start
    ).options(selectinload(MealPlan.meals).selectinload(PlannedMeal.recipe))
    
    result = await session.execute(statement)
    plan = result.scalar_one_or_none()
    
    if plan:
        return plan
    
    # Create new plan
    new_plan = MealPlan(
        id=plan_id or str(uuid4()),
        user_id=user_id,
        week_start=week_start
    )
    session.add(new_plan)
    await session.flush()
    
    # Reload with relationships
    result = await session.execute(
        select(MealPlan).where(MealPlan.id == new_plan.id).options(
            selectinload(MealPlan.meals).selectinload(PlannedMeal.recipe)
        )
    )
    return result.scalar_one()


async def add_planned_meal(
    session: AsyncSession,
    plan_id: str,
    user_id: str,
    recipe_id: str,
    date: str,
    meal_type: str,
    servings: int = 1,
    notes: str = None
) -> Optional[PlannedMeal]:
    """Add a meal to the plan"""
    # Verify plan belongs to user
    statement = select(MealPlan).where(
        MealPlan.id == plan_id,
        MealPlan.user_id == user_id
    )
    result = await session.execute(statement)
    if not result.scalar_one_or_none():
        return None
    
    meal = PlannedMeal(
        plan_id=plan_id,
        recipe_id=recipe_id,
        date=date,
        meal_type=meal_type,
        servings=servings,
        notes=notes
    )
    session.add(meal)
    await session.flush()
    
    # Reload with recipe
    statement = select(PlannedMeal).where(
        PlannedMeal.id == meal.id
    ).options(selectinload(PlannedMeal.recipe))
    result = await session.execute(statement)
    return result.scalar_one()


async def update_planned_meal(
    session: AsyncSession,
    meal_id: int,
    user_id: str,
    recipe_id: Optional[str] = None,
    date: Optional[str] = None,
    meal_type: Optional[str] = None,
    servings: Optional[int] = None,
    notes: Optional[str] = None
) -> Optional[PlannedMeal]:
    """Update a planned meal"""
    # Verify meal belongs to user's plan
    statement = select(PlannedMeal).join(MealPlan).where(
        PlannedMeal.id == meal_id,
        MealPlan.user_id == user_id
    ).options(selectinload(PlannedMeal.recipe))
    
    result = await session.execute(statement)
    meal = result.scalar_one_or_none()
    
    if not meal:
        return None
    
    if recipe_id is not None:
        meal.recipe_id = recipe_id
    if date is not None:
        meal.date = date
    if meal_type is not None:
        meal.meal_type = meal_type
    if servings is not None:
        meal.servings = servings
    if notes is not None:
        meal.notes = notes
    
    await session.flush()
    
    # Reload with recipe
    statement = select(PlannedMeal).where(
        PlannedMeal.id == meal_id
    ).options(selectinload(PlannedMeal.recipe))
    result = await session.execute(statement)
    return result.scalar_one()


async def delete_planned_meal(
    session: AsyncSession,
    meal_id: int,
    user_id: str
) -> bool:
    """Delete a planned meal"""
    statement = select(PlannedMeal).join(MealPlan).where(
        PlannedMeal.id == meal_id,
        MealPlan.user_id == user_id
    )
    result = await session.execute(statement)
    meal = result.scalar_one_or_none()
    
    if not meal:
        return False
    
    await session.delete(meal)
    await session.flush()
    return True


async def get_week_recipes(
    session: AsyncSession,
    plan_id: str,
    user_id: str
) -> List[SavedRecipe]:
    """Get all recipes from a meal plan for shopping list generation"""
    statement = select(SavedRecipe).join(PlannedMeal).join(MealPlan).where(
        PlannedMeal.plan_id == plan_id,
        MealPlan.user_id == user_id
    ).distinct()
    
    result = await session.execute(statement)
    return list(result.scalars().all())


# ============== Barcode Cache CRUD ==============

async def get_barcode_cache(
    session: AsyncSession,
    barcode: str
) -> Optional[BarcodeCache]:
    """Get cached barcode data"""
    statement = select(BarcodeCache).where(BarcodeCache.barcode == barcode)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def set_barcode_cache(
    session: AsyncSession,
    barcode: str,
    product_data: dict
) -> BarcodeCache:
    """Cache barcode data (upsert)"""
    existing = await get_barcode_cache(session, barcode)
    
    if existing:
        existing.product_data = json.dumps(product_data)
        existing.cached_at = datetime.utcnow()
        await session.flush()
        return existing
    
    cache = BarcodeCache(
        barcode=barcode,
        product_data=json.dumps(product_data)
    )
    session.add(cache)
    await session.flush()
    return cache


# ============== Auth Token CRUD ==============

async def store_refresh_token(
    session: AsyncSession,
    jti: str,
    user_id: str,
    expires_at: str
) -> RefreshToken:
    """Store a refresh token in the database"""
    token = RefreshToken(
        jti=jti,
        user_id=user_id,
        expires_at=datetime.fromisoformat(expires_at)
    )
    session.add(token)
    await session.flush()
    return token


async def get_refresh_token(
    session: AsyncSession,
    jti: str
) -> Optional[RefreshToken]:
    """Get a refresh token by its JTI"""
    statement = select(RefreshToken).where(RefreshToken.jti == jti)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def delete_refresh_token(
    session: AsyncSession,
    jti: str
) -> bool:
    """Delete a refresh token (used during token rotation)"""
    token = await get_refresh_token(session, jti)
    if not token:
        return False
    await session.delete(token)
    await session.flush()
    return True


async def delete_user_refresh_tokens(
    session: AsyncSession,
    user_id: str
) -> None:
    """Delete all refresh tokens for a user (used during logout)"""
    await session.execute(
        delete(RefreshToken).where(RefreshToken.user_id == user_id)
    )
    await session.flush()


async def blacklist_token(
    session: AsyncSession,
    jti: str,
    token_type: str,
    expires_at: str
) -> BlacklistedToken:
    """Add a token to the blacklist"""
    # Check if already blacklisted
    statement = select(BlacklistedToken).where(BlacklistedToken.jti == jti)
    result = await session.execute(statement)
    existing = result.scalar_one_or_none()
    
    if existing:
        return existing
    
    token = BlacklistedToken(
        jti=jti,
        token_type=token_type,
        expires_at=datetime.fromisoformat(expires_at)
    )
    session.add(token)
    await session.flush()
    return token


async def is_token_blacklisted(
    session: AsyncSession,
    jti: str
) -> bool:
    """Check if a token is blacklisted"""
    statement = select(BlacklistedToken).where(BlacklistedToken.jti == jti)
    result = await session.execute(statement)
    return result.scalar_one_or_none() is not None


async def cleanup_expired_tokens(session: AsyncSession) -> None:
    """Remove expired tokens from refresh_tokens and blacklisted_tokens tables"""
    now = datetime.utcnow()
    await session.execute(
        delete(RefreshToken).where(RefreshToken.expires_at < now)
    )
    await session.execute(
        delete(BlacklistedToken).where(BlacklistedToken.expires_at < now)
    )
    await session.flush()


# ============== LLM Usage CRUD ==============

async def get_llm_usage(
    session: AsyncSession,
    user_id: str,
    endpoint: Optional[str] = None,
    usage_date: Optional[date] = None
) -> List[LLMUsage]:
    """
    Get LLM usage records for a user.
    
    Args:
        session: Database session
        user_id: User ID
        endpoint: Optional endpoint name to filter by
        usage_date: Optional date to filter by (defaults to today)
    
    Returns:
        List of LLMUsage records
    """
    from datetime import date as date_type
    
    stmt = select(LLMUsage).where(LLMUsage.user_id == user_id)
    
    if endpoint:
        stmt = stmt.where(LLMUsage.endpoint == endpoint)
    
    if usage_date:
        stmt = stmt.where(LLMUsage.date == usage_date)
    
    result = await session.execute(stmt)
    return list(result.scalars().all())

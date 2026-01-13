"""
Models package - exports all Pydantic models and SQLModel tables.
"""

# Pydantic models for API
from app.models.user import (
    UserBase, UserCreate, UserLogin, UserUpdate, UserPasswordUpdate,
    User, UserInDB, Token, TokenPair, TokenData, RefreshTokenRequest
)
from app.models.family import (
    Role, ConditionType, HealthCondition, FamilyMember, FamilyProfile
)
from app.models.recipe import (
    VerdictType, Substitution, Adaptation, MemberVerdict, 
    RecipeAnalysis, RecipeRequest
)
from app.models.saved_recipe import (
    SaveRecipeRequest, UpdateRecipeRequest, SavedRecipe,
    SavedRecipeResponse, SavedRecipesListResponse
)
from app.models.shopping import (
    ShoppingItem, CreateShoppingListRequest, GenerateShoppingListRequest,
    AddItemRequest, UpdateItemRequest, ShoppingList, ShoppingListResponse,
    ShoppingListsResponse, ExtractedIngredient
)
from app.models.meal_plan import (
    MealType, PlannedMeal, AddMealRequest, UpdateMealRequest,
    MealPlan, MealPlanResponse, GenerateShoppingFromPlanRequest
)

# SQLModel table models
from app.models.tables import (
    User as UserTable,
    FamilyMember as FamilyMemberTable,
    HealthCondition as HealthConditionTable,
    PantryItem,
    SavedRecipe as SavedRecipeTable,
    RecipeTag,
    ShoppingList as ShoppingListTable,
    ShoppingItem as ShoppingItemTable,
    MealPlan as MealPlanTable,
    PlannedMeal as PlannedMealTable,
    BarcodeCache,
    RefreshToken,
    BlacklistedToken,
    LLMUsage,
    UserRead, FamilyMemberRead, HealthConditionRead
)

__all__ = [
    # User models
    "UserBase", "UserCreate", "UserLogin", "UserUpdate", "UserPasswordUpdate",
    "User", "UserInDB", "Token", "TokenPair", "TokenData", "RefreshTokenRequest",
    # Family models
    "Role", "ConditionType", "HealthCondition", "FamilyMember", "FamilyProfile",
    # Recipe models
    "VerdictType", "Substitution", "Adaptation", "MemberVerdict",
    "RecipeAnalysis", "RecipeRequest",
    # Saved recipe models
    "SaveRecipeRequest", "UpdateRecipeRequest", "SavedRecipe",
    "SavedRecipeResponse", "SavedRecipesListResponse",
    # Shopping models
    "ShoppingItem", "CreateShoppingListRequest", "GenerateShoppingListRequest",
    "AddItemRequest", "UpdateItemRequest", "ShoppingList", "ShoppingListResponse",
    "ShoppingListsResponse", "ExtractedIngredient",
    # Meal plan models
    "MealType", "PlannedMeal", "AddMealRequest", "UpdateMealRequest",
    "MealPlan", "MealPlanResponse", "GenerateShoppingFromPlanRequest",
    # SQLModel tables
    "UserTable", "FamilyMemberTable", "HealthConditionTable", "PantryItem",
    "SavedRecipeTable", "RecipeTag", "ShoppingListTable", "ShoppingItemTable",
    "MealPlanTable", "PlannedMealTable", "BarcodeCache", "RefreshToken",
    "BlacklistedToken", "LLMUsage", "UserRead", "FamilyMemberRead", "HealthConditionRead"
]

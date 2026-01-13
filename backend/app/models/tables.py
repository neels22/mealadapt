"""
SQLModel table definitions for PostgreSQL database.
All database tables are defined here with their relationships.
"""
from __future__ import annotations

import os
from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING
from enum import Enum
from uuid import uuid4
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint
from dotenv import load_dotenv
import json

load_dotenv()

# Type alias to avoid name conflict with field name 'date'
if TYPE_CHECKING:
    from datetime import date as DateType
else:
    DateType = date

# Schema configuration - matches database.py
SCHEMA_NAME = os.getenv("DB_SCHEMA", "mealadapt")


# ============== Enums ==============

class Role(str, Enum):
    ADULT = "Adult"
    CHILD = "Child"
    BABY = "Baby"


class ConditionType(str, Enum):
    DIABETES = "Diabetes"
    HIGH_URIC_ACID = "High Uric Acid"
    HYPERTENSION = "Hypertension"
    HEART_DISEASE = "Heart Disease"
    KIDNEY_DISEASE = "Kidney Disease"
    CELIAC = "Celiac (Gluten-Free)"
    LACTOSE_INTOLERANCE = "Lactose Intolerance"
    PEANUT_ALLERGY = "Peanut Allergy"


class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


# ============== User Tables ==============

class User(SQLModel, table=True):
    """User account table"""
    __tablename__ = "users"
    __table_args__ = {"schema": SCHEMA_NAME}
    
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    name: str
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    family_members: List["FamilyMember"] = Relationship(back_populates="user", cascade_delete=True)
    pantry_items: List["PantryItem"] = Relationship(back_populates="user", cascade_delete=True)
    saved_recipes: List["SavedRecipe"] = Relationship(back_populates="user", cascade_delete=True)
    shopping_lists: List["ShoppingList"] = Relationship(back_populates="user", cascade_delete=True)
    meal_plans: List["MealPlan"] = Relationship(back_populates="user", cascade_delete=True)
    refresh_tokens: List["RefreshToken"] = Relationship(back_populates="user", cascade_delete=True)
    llm_usage: List["LLMUsage"] = Relationship(back_populates="user", cascade_delete=True)


# ============== Family Tables ==============

class FamilyMember(SQLModel, table=True):
    """Family member table"""
    __tablename__ = "family_members"
    __table_args__ = {"schema": SCHEMA_NAME}
    
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: Optional[str] = Field(default=None, foreign_key=f"{SCHEMA_NAME}.users.id", index=True)
    name: str
    avatar: str = Field(default="😊")
    role: Role = Field(default=Role.ADULT)
    custom_restrictions: Optional[str] = None  # JSON array string
    preferences: Optional[str] = None  # JSON object string
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="family_members")
    conditions: List["HealthCondition"] = Relationship(back_populates="member", cascade_delete=True)
    
    def get_custom_restrictions(self) -> List[str]:
        """Parse custom_restrictions JSON string to list"""
        if self.custom_restrictions:
            return json.loads(self.custom_restrictions)
        return []
    
    def set_custom_restrictions(self, restrictions: List[str]):
        """Serialize list to JSON string"""
        self.custom_restrictions = json.dumps(restrictions)
    
    def get_preferences(self) -> Optional[dict]:
        """Parse preferences JSON string to dict"""
        if self.preferences:
            return json.loads(self.preferences)
        return None
    
    def set_preferences(self, prefs: Optional[dict]):
        """Serialize dict to JSON string"""
        self.preferences = json.dumps(prefs) if prefs else None


class HealthCondition(SQLModel, table=True):
    """Health conditions for family members"""
    __tablename__ = "health_conditions"
    __table_args__ = {"schema": SCHEMA_NAME}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    member_id: str = Field(foreign_key=f"{SCHEMA_NAME}.family_members.id", index=True)
    condition_type: ConditionType
    enabled: bool = Field(default=False)
    notes: Optional[str] = None
    
    # Relationships
    member: FamilyMember = Relationship(back_populates="conditions")


# ============== Pantry Tables ==============

class PantryItem(SQLModel, table=True):
    """Pantry items table"""
    __tablename__ = "pantry_items"
    __table_args__ = {"schema": SCHEMA_NAME}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[str] = Field(default=None, foreign_key=f"{SCHEMA_NAME}.users.id", index=True)
    name: str
    category: Optional[str] = None
    added_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="pantry_items")


# ============== Recipe Tables ==============

class SavedRecipe(SQLModel, table=True):
    """Saved recipes table"""
    __tablename__ = "saved_recipes"
    __table_args__ = {"schema": SCHEMA_NAME}
    
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(foreign_key=f"{SCHEMA_NAME}.users.id", index=True)
    dish_name: str
    recipe_text: Optional[str] = None
    analysis_json: Optional[str] = None  # JSON string
    is_favorite: bool = Field(default=False)
    notes: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="saved_recipes")
    tags: List["RecipeTag"] = Relationship(back_populates="recipe", cascade_delete=True)
    planned_meals: List["PlannedMeal"] = Relationship(back_populates="recipe")
    
    def get_analysis(self) -> Optional[dict]:
        """Parse analysis_json to dict"""
        if self.analysis_json:
            return json.loads(self.analysis_json)
        return None
    
    def set_analysis(self, analysis: dict):
        """Serialize analysis dict to JSON"""
        self.analysis_json = json.dumps(analysis)


class RecipeTag(SQLModel, table=True):
    """Tags for saved recipes"""
    __tablename__ = "recipe_tags"
    __table_args__ = {"schema": SCHEMA_NAME}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    recipe_id: str = Field(foreign_key=f"{SCHEMA_NAME}.saved_recipes.id", index=True)
    tag: str
    
    # Relationships
    recipe: SavedRecipe = Relationship(back_populates="tags")


# ============== Shopping Tables ==============

class ShoppingList(SQLModel, table=True):
    """Shopping lists table"""
    __tablename__ = "shopping_lists"
    __table_args__ = {"schema": SCHEMA_NAME}
    
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(foreign_key=f"{SCHEMA_NAME}.users.id", index=True)
    name: str
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Relationships
    user: User = Relationship(back_populates="shopping_lists")
    items: List["ShoppingItem"] = Relationship(back_populates="shopping_list", cascade_delete=True)


class ShoppingItem(SQLModel, table=True):
    """Items in shopping lists"""
    __tablename__ = "shopping_items"
    __table_args__ = {"schema": SCHEMA_NAME}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    list_id: str = Field(foreign_key=f"{SCHEMA_NAME}.shopping_lists.id", index=True)
    ingredient: str
    quantity: Optional[str] = None
    category: Optional[str] = None
    is_checked: bool = Field(default=False)
    source_recipe_id: Optional[str] = None
    
    # Relationships
    shopping_list: ShoppingList = Relationship(back_populates="items")


# ============== Meal Plan Tables ==============

class MealPlan(SQLModel, table=True):
    """Weekly meal plans table"""
    __tablename__ = "meal_plans"
    __table_args__ = {"schema": SCHEMA_NAME}
    
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(foreign_key=f"{SCHEMA_NAME}.users.id", index=True)
    week_start: str  # DATE as YYYY-MM-DD string
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="meal_plans")
    meals: List["PlannedMeal"] = Relationship(back_populates="plan", cascade_delete=True)


class PlannedMeal(SQLModel, table=True):
    """Planned meals within a meal plan"""
    __tablename__ = "planned_meals"
    __table_args__ = {"schema": SCHEMA_NAME}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    plan_id: str = Field(foreign_key=f"{SCHEMA_NAME}.meal_plans.id", index=True)
    recipe_id: Optional[str] = Field(default=None, foreign_key=f"{SCHEMA_NAME}.saved_recipes.id")
    date: str  # DATE as YYYY-MM-DD string
    meal_type: str  # MealType value
    servings: int = Field(default=1)
    notes: Optional[str] = None
    
    # Relationships
    plan: MealPlan = Relationship(back_populates="meals")
    recipe: Optional[SavedRecipe] = Relationship(back_populates="planned_meals")


# ============== Cache Tables ==============

class BarcodeCache(SQLModel, table=True):
    """Barcode product data cache"""
    __tablename__ = "barcode_cache"
    __table_args__ = {"schema": SCHEMA_NAME}
    
    barcode: str = Field(primary_key=True)
    product_data: str  # JSON string
    cached_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    def get_product_data(self) -> dict:
        """Parse product_data JSON to dict"""
        return json.loads(self.product_data)
    
    def set_product_data(self, data: dict):
        """Serialize dict to JSON"""
        self.product_data = json.dumps(data)


# ============== Auth Token Tables ==============

class RefreshToken(SQLModel, table=True):
    """Refresh tokens for JWT authentication"""
    __tablename__ = "refresh_tokens"
    __table_args__ = {"schema": SCHEMA_NAME}
    
    jti: str = Field(primary_key=True)  # JWT ID
    user_id: str = Field(foreign_key=f"{SCHEMA_NAME}.users.id", index=True)
    expires_at: datetime
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="refresh_tokens")


class BlacklistedToken(SQLModel, table=True):
    """Blacklisted/revoked tokens"""
    __tablename__ = "blacklisted_tokens"
    __table_args__ = {"schema": SCHEMA_NAME}
    
    jti: str = Field(primary_key=True)  # JWT ID
    token_type: str  # "access" or "refresh"
    expires_at: datetime
    blacklisted_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


# ============== Rate Limiting Tables ==============

class LLMUsage(SQLModel, table=True):
    """Track LLM API calls per user per endpoint per day"""
    __tablename__ = "llm_usage"
    __table_args__ = (
        UniqueConstraint('user_id', 'endpoint', 'date', name='uq_user_endpoint_date'),
        {"schema": SCHEMA_NAME}
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key=f"{SCHEMA_NAME}.users.id", index=True)
    endpoint: str = Field(index=True)
    date: DateType = Field(default_factory=lambda: date.today(), index=True)
    call_count: int = Field(default=0)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="llm_usage")


# ============== Response Models (non-table) ==============

class UserRead(SQLModel):
    """User response model (without password)"""
    id: str
    email: str
    name: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class FamilyMemberRead(SQLModel):
    """Family member response with parsed JSON fields"""
    id: str
    name: str
    avatar: str
    role: Role
    conditions: List["HealthConditionRead"] = []
    custom_restrictions: List[str] = []
    preferences: Optional[dict] = None


class HealthConditionRead(SQLModel):
    """Health condition response model"""
    type: ConditionType
    enabled: bool
    notes: Optional[str] = None

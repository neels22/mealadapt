import uuid
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


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


class HealthCondition(BaseModel):
    type: ConditionType
    enabled: bool = False
    notes: Optional[str] = None


class FamilyMember(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    avatar: str = "😊"
    role: Role = Role.ADULT
    conditions: List[HealthCondition] = []
    custom_restrictions: List[str] = []
    preferences: Optional[dict] = None


class FamilyProfile(BaseModel):
    members: List[FamilyMember] = []

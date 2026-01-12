from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class VerdictType(str, Enum):
    SAFE = "safe"
    NEEDS_ADAPTATION = "needs_adaptation"
    NOT_RECOMMENDED = "not_recommended"


class Substitution(BaseModel):
    original: str
    replacement: str
    reason: str


class Adaptation(BaseModel):
    modifications: List[str] = []
    substitutions: List[Substitution] = []
    preparation_changes: List[str] = []


class MemberVerdict(BaseModel):
    member_id: str
    member_name: str
    verdict: VerdictType
    reasons: List[str] = []
    concerns: List[str] = []
    adaptations: Optional[Adaptation] = None
    nutritional_notes: Optional[str] = None


class RecipeAnalysis(BaseModel):
    dish_name: str
    base_description: str
    overall_safety: str
    member_verdicts: List[MemberVerdict]
    general_tips: List[str] = []


class RecipeRequest(BaseModel):
    recipe_text: str
    family_profile: dict

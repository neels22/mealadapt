from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator


class OverallSafety(str, Enum):
    SAFE = "safe"
    CAUTION = "caution"
    UNSAFE = "unsafe"


class VerdictType(str, Enum):
    SAFE = "safe"
    NEEDS_ADAPTATION = "needs_adaptation"
    NOT_RECOMMENDED = "not_recommended"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Substitution(StrictModel):
    original: str
    replacement: str
    reason: str


class Adaptation(StrictModel):
    modifications: List[str] = Field(default_factory=list)
    substitutions: List[Substitution] = Field(default_factory=list)
    preparation_changes: List[str] = Field(default_factory=list)

    def is_empty(self) -> bool:
        return not (self.modifications or self.substitutions or self.preparation_changes)


class MemberVerdict(StrictModel):
    member_id: str
    member_name: str
    verdict: VerdictType
    reasons: List[str] = Field(default_factory=list)
    concerns: List[str] = Field(default_factory=list)
    adaptations: Optional[Adaptation] = None
    nutritional_notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_adaptations(self):
        if self.verdict == VerdictType.NEEDS_ADAPTATION:
            if self.adaptations is None or self.adaptations.is_empty():
                raise ValueError("adaptations must be present and non-empty when verdict=needs_adaptation")
        return self


class RecipeAnalysis(StrictModel):
    dish_name: str
    base_description: str
    overall_safety: OverallSafety
    member_verdicts: List[MemberVerdict]
    general_tips: List[str] = Field(default_factory=list)


class RecipeRequest(StrictModel):
    recipe_text: str
    family_profile: dict

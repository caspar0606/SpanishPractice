from typing import Optional

from pydantic import BaseModel

from src.domain.enums import OnboardingStep
from src.domain.models.profile import PlacementForm, PlacementSubmission, UserGoals
from src.domain.models.user import User


class PlanSummary(BaseModel):
    current_band: str
    current_gloss: str
    target_band: Optional[str] = None
    target_gloss: Optional[str] = None
    half_steps_remaining: Optional[int] = None
    estimated_weeks: Optional[int] = None


class OnboardingStatusResponse(BaseModel):
    step: OnboardingStep
    goals: Optional[UserGoals] = None
    plan: PlanSummary


class GoalsRequest(BaseModel):
    username: str
    goals: UserGoals


class GoalsResponse(BaseModel):
    user: User
    step: OnboardingStep
    plan: PlanSummary


class PlacementFormResponse(BaseModel):
    form: PlacementForm


class PlacementSubmitRequest(BaseModel):
    username: str
    submission: PlacementSubmission


class PlacementSubmitResponse(BaseModel):
    assigned_band: str
    gloss: str
    mcq_correct: int
    mcq_total: int
    notes_en: str
    plan: PlanSummary

from pydantic import BaseModel, Field

from src.domain.enums import ExerciseStyle, ExerciseTypes, RecommendationKind
from src.domain.models.exercise import AreasOfFocus


class Recommendation(BaseModel):
    """One suggested next exercise. The learner taps it to start generating."""

    kind: RecommendationKind
    type: ExerciseTypes
    style: ExerciseStyle = ExerciseStyle.PREFERENCES
    focus: AreasOfFocus
    estimated_minutes: int
    title_en: str
    reason_en: str
    kind_label: str


class DailySlot(BaseModel):
    """One of the four once-a-day skills on the home screen."""

    type: ExerciseTypes
    done: bool
    title_en: str
    reason_en: str
    kind_label: str
    estimated_minutes: int = 0
    style: ExerciseStyle = ExerciseStyle.PREFERENCES
    focus: AreasOfFocus = Field(default_factory=AreasOfFocus)


class HomePlan(BaseModel):
    remaining: int
    complete: bool
    daily: list[DailySlot]
    extras: list[Recommendation] = Field(default_factory=list)

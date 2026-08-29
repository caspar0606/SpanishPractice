from pydantic import BaseModel

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

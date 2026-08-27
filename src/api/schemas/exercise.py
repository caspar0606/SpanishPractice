from pydantic import BaseModel

from src.domain.enums import ExerciseStyle, ExerciseTypes
from src.domain.models.exercise import AreasOfFocus, Exercise, ExerciseContext

class ExerciseRequest(BaseModel):
    """Difficulty is derived from the learner's band, never sent by the client."""

    username: str
    type: ExerciseTypes
    style: ExerciseStyle
    preferences: AreasOfFocus | None = None

class ExerciseResponse(BaseModel):
    exercise: Exercise





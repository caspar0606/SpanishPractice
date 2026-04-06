from pydantic import BaseModel

from src.domain.enums import DifficultyLevels, ExerciseStyle, ExerciseTypes
from src.domain.models.exercise import AreasOfFocus, Exercise, ExerciseContext

class ExerciseRequest(BaseModel):
    username: str
    type: ExerciseTypes
    difficulty: DifficultyLevels
    style: ExerciseStyle
    preferences: AreasOfFocus | None = None

class ExerciseResponse(BaseModel):
    exercise: Exercise





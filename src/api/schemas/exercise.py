from datetime import date

from pydantic import BaseModel, Field

from src.domain.enums import ExerciseStyle, ExerciseTypes, LengthPreference
from src.domain.models.exercise import AreasOfFocus, Exercise, ExerciseContext
from src.domain.models.recommendation import DailySlot, Recommendation


class ExerciseRequest(BaseModel):
    """Difficulty is derived from the learner's band, never sent by the client."""

    username: str = ""
    type: ExerciseTypes
    style: ExerciseStyle
    preferences: AreasOfFocus | None = None
    length: LengthPreference | None = None
    replace: bool = False


class ExerciseResponse(BaseModel):
    exercise: Exercise


class RecommendRequest(BaseModel):
    username: str = ""
    day: date | None = None
    tz_offset_minutes: int | None = Field(default=None, ge=-960, le=960)


class RecommendResponse(BaseModel):
    remaining: int
    complete: bool
    daily: list[DailySlot]
    extras: list[Recommendation] = []
    cards: list[Recommendation] = []






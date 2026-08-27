from datetime import datetime
from typing import ClassVar, Optional

from pydantic import BaseModel, Field

from src.domain.enums import Band, Direction, LengthPreference, WeeklyTime


class UserGoals(BaseModel):
    """Why the learner is here. Set once at onboarding, editable later."""

    _EXAMPLE: ClassVar[dict] = {
        "direction": "travel",
        "desired_band": "A2",
        "weekly_time": "1-2h",
        "length_preference": "standard",
    }

    direction: Direction
    desired_band: Band
    weekly_time: WeeklyTime
    length_preference: LengthPreference = LengthPreference.STANDARD

    @classmethod
    def example_json(cls) -> dict:
        return cls._EXAMPLE.copy()


class Proficiency(BaseModel):
    """Top-level ability. Moves slowly and only on genuine evidence."""

    current: Band = Band.A1
    updated_at: Optional[datetime] = None
    genuine_attempts_at_band: int = 0
    evidence_score: float = 0.0


class PlacementResult(BaseModel):
    """Outcome of the one-off placement test."""

    completed: bool = False
    mcq_correct: int = 0
    mcq_total: int = 0
    writing_signal: float = 0.0
    reading_signal: float = 0.0
    assigned_band: Optional[Band] = None
    taken_at: Optional[datetime] = None


class PlacementMcqItem(BaseModel):
    """One multiple-choice placement question, served without the answer."""

    id: str
    band: Band
    prompt: str
    options: list[str]


class PlacementForm(BaseModel):
    """What the learner is asked to complete."""

    mcq: list[PlacementMcqItem]
    writing_prompt_en: str
    writing_target_words: int
    reading_passage: str
    reading_questions: list[str]


class PlacementSubmission(BaseModel):
    """Raw learner answers coming back from the UI."""

    mcq_answers: dict[str, str] = Field(default_factory=dict)
    writing_response: str = ""
    reading_answers: list[str] = Field(default_factory=list)

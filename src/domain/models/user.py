from typing import Optional

from pydantic import BaseModel, Field

from src.domain.enums import Skill
from src.domain.models.chat import ChatTurn
from src.domain.models.exercise import ExerciseStorage
from src.domain.models.profile import PlacementResult, Proficiency, UserGoals
from src.domain.models.progress import Progress, ProgressUpdates, SkillProgress
from src.domain.models.vocab import VocabEntry

SCHEMA_VERSION = 2


class User(BaseModel):
    schema_version: int = SCHEMA_VERSION
    name: str
    # Cross-skill concept totals. Per-skill breakdowns live in `skills`.
    progress: Progress
    first_time: bool
    goals: Optional[UserGoals] = None
    proficiency: Proficiency = Field(default_factory=Proficiency)
    placement: PlacementResult = Field(default_factory=PlacementResult)
    skills: dict[Skill, SkillProgress] = Field(default_factory=dict)
    vocab: list[VocabEntry] = Field(default_factory=list)
    chat_history: list[ChatTurn] = Field(default_factory=list)
    current_exercise: Optional[ExerciseStorage] = None
    exercise_history: list[ExerciseStorage] = Field(default_factory=list)
    progress_history: list[ProgressUpdates] = Field(default_factory=list)

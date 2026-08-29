from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.domain.enums import Band, RelativeLevel, Skill
from src.domain.models.progress import Progress, ProgressUpdates


class ConceptRow(BaseModel):
    """One tracked concept, ready to render."""

    key: str
    label: str
    total_attempts: float
    correct_attempts: float
    score: float
    practised: bool


class SkillRow(BaseModel):
    skill: Skill
    label: str
    relative_level: RelativeLevel
    relative_label: str
    genuine_attempts: int
    total_attempts: int
    accuracy: float
    last_practised: Optional[datetime] = None


class BandSummary(BaseModel):
    band: Band
    gloss: str
    genuine_attempts_at_band: int
    attempts_until_review: int
    # Current accuracy across skills, against the accuracy a move up needs.
    evidence_score: float
    target_accuracy: float


class ProgressOverview(BaseModel):
    """The three layers: overall band, per-skill standing, per-concept detail."""

    overall: BandSummary
    skills: list[SkillRow]
    tenses: list[ConceptRow]
    grammar: list[ConceptRow]
    topics: list[ConceptRow]
    genuine_attempts: int
    total_attempts: int


class CurrentProgressRequest(BaseModel):
    username: str

class CurrentProgressResponse(BaseModel):
    progress: Progress
    overview: ProgressOverview

class HistoricalProgressRequest(BaseModel):
    username: str

class HistoricalProgressResponse(BaseModel):
    progress: Progress
    progress_history: list[ProgressUpdates]

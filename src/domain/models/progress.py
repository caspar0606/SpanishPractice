
from datetime import datetime

from pydantic import BaseModel

from src.domain.enums import Grammar, Tenses, Topics


class ComputeStats(BaseModel):
    total_attempts: float = 0
    correct_attempts: float = 0

class Progress(BaseModel):
    tenses: dict[Tenses, ComputeStats]
    grammar: dict[Grammar, ComputeStats] 
    topics: dict[Topics, ComputeStats]

class ProgressUpdates(BaseModel):
    id: str
    exercise_id: str
    time: datetime
    score: Progress
    new_progress: Progress



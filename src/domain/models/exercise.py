from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.domain.enums import DifficultyLevels, ExerciseTypes, Grammar, Tenses, Topics


class AreasOfFocus(BaseModel):
    focus_tenses: Optional[list[Tenses]] = None
    focus_grammar: Optional[list[Grammar]] = None
    focus_topics: Optional[list[Topics]] = None

class Exercise(BaseModel):
    id: str
    exercise_type: ExerciseTypes
    difficulty_level: DifficultyLevels
    areas_of_focus: AreasOfFocus
    start_time: datetime
    end_time: Optional[datetime] = None

class LessonTopics(BaseModel):
    areas_of_focus: AreasOfFocus
    difficulty: DifficultyLevels 
    word_count: int
from typing import Optional
from pydantic import BaseModel
from src.domain.classes import Exercise
from src.domain.preferences import DIFFICULTY_CONFIG
from src.domain.enums import Tenses, Grammar, Topics
from src.llm.enums import AgentNames

class LessonTopics(BaseModel):
    topics: Optional[list[Topics]] = None
    grammar: Optional[list[Grammar]] = None
    tenses: Optional[list[Tenses]] = None
    word_count: int

class AgentInputs(BaseModel):
    name: AgentNames
    lesson_topics: Optional[str] = None
    system_prompt: str
    input_text: Optional[str] = None
    output_schema: Optional[dict] = None


def lesson_topics(exercise: Exercise | None):
    if exercise:
        lesson_topics = LessonTopics(
            topics=exercise.focus_topics,
            grammar=exercise.focus_grammar,
            tenses=exercise.focus_tenses,
            word_count= DIFFICULTY_CONFIG[exercise.difficulty_level].word_count) 
            
        return lesson_topics.model_dump_json()
    
    else: 
        return 
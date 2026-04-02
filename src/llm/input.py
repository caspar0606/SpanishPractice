from typing import Optional, Union
from pydantic import BaseModel
from src.domain.preferences import DIFFICULTY_CONFIG, DifficultyLevels
from src.domain.enums import Tenses, Grammar, Topics
from src.llm.enums import AgentNames
from src.llm.output import ReadingGeneration

LLMStimulus = Union[ReadingGeneration,list[str], str]
LLMInput = Union[str, list[str], ]

class LessonTopics(BaseModel):
    topics: Optional[list[Topics]] = None
    grammar: Optional[list[Grammar]] = None
    tenses: Optional[list[Tenses]] = None
    difficulty: Optional[DifficultyLevels] = None
    word_count: int

class ModelInputs(BaseModel):
    model_name: str
    temperature: float
    max_tokens: Optional[int]

class AgentInputs(BaseModel):
    name: AgentNames
    lesson_topics: Optional[LessonTopics] = None
    system_prompt: str
    stimulus: Optional[LLMStimulus] = None
    input_text: Optional[LLMInput] = None
    output_schema: type[BaseModel] | None = None

from src.domain.classes import Exercise

def lesson_topics(exercise: Exercise):

    lesson_topics = LessonTopics(
        topics=exercise.areas_of_focus.focus_topics,
        grammar=exercise.areas_of_focus.focus_grammar,
        tenses=exercise.areas_of_focus.focus_tenses,
        word_count=(DIFFICULTY_CONFIG[exercise.difficulty_level].w_word_count if exercise.exercise_type == "writing" 
                    else DIFFICULTY_CONFIG[exercise.difficulty_level].r_word_count),
    difficulty=exercise.difficulty_level
    )
        
    return lesson_topics

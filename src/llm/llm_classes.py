from typing import Optional
from pydantic import BaseModel
from src.domain.classes import Exercise
from src.domain.preferences import DIFFICULTY_CONFIG
from src.domain.enums import Tenses, Grammar, Topics, DifficultyLevels

class LLMPrompt(BaseModel):
    topics: Optional[list[Topics]] = None
    grammar: Optional[list[Grammar]] = None
    tenses: Optional[list[Tenses]] = None
    word_count: int
    

def prompt_formatter(exercise: Exercise):
    prompt = LLMPrompt(
        topics=exercise.focus_topics,
        grammar=exercise.focus_grammar,
        tenses=exercise.focus_tenses,
        word_count= DIFFICULTY_CONFIG[exercise.difficulty_level].word_count) 
        
    return prompt.model_dump_json()
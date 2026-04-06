from typing import Optional

from pydantic import BaseModel
from src.domain.classes import ComputeStats, Tenses, Grammar, Topics
from src.llm.enums import DrillTypes


##WRITING
class Edit(BaseModel):
    original_text: str
    corrected_text: str
    reason: str

class WritingCorrection(BaseModel):
    corrected_version: str
    tense_errors: dict[Tenses, list[Edit]]
    grammar_errors: dict[Grammar, list[Edit]]
    topic_errors: dict[Topics, list[Edit]]
    typos: list[Edit]
    other_mistakes: list[Edit]

class WritingSummary(BaseModel):
    tense_edits: str
    grammar_edits: str
    topic_edits: str
    general_feedback: str


##READING
class ReadingGeneration(BaseModel):
    passage: str
    questions: list[str]

class QuestionMarking(BaseModel):
    individual_questions: list[str]
    general_feedback: str


##DRILLS
class DrillItem(BaseModel):
    prompt: str
    answer: str
    options: list[str] | None = None

class DrillSet(BaseModel):
    drill_type: DrillTypes
    drills: list[DrillItem]

class Drills(BaseModel):
    drill_sets: dict[DrillTypes, DrillSet]

class DrillMarking(BaseModel):
    prompt: str
    answer: str
    user_response: str
    comment: Optional[str] 
    is_correct: bool

class DrillMarkingSet(BaseModel):
    drill_type: DrillTypes
    marked_drills: list[DrillMarking]
    stats: ComputeStats = ComputeStats() 

class MarkedDrills(BaseModel):
    marked_drill_sets: list[DrillMarkingSet]
    stats: ComputeStats

class UserDrillResponses(BaseModel):
    responses: dict[DrillTypes, list[str]]




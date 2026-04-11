from pydantic import BaseModel

from src.infrastructure.llm.contracts.shared import TextCorrection

class ReadingGeneration(BaseModel):
    passage: str
    questions: list[str]

class TextCorrections(BaseModel):
    corrections: list[TextCorrection]

class QuestionMarking(BaseModel):
    individual_questions: list[str]
    general_feedback: str
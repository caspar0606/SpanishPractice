from pydantic import BaseModel, Field

from src.infrastructure.llm.contracts.text_correction import TextCorrection

class ReadingGeneration(BaseModel):
    passage: str
    questions: list[str] = Field(min_length=5, max_length=5)

class TextCorrections(BaseModel):
    corrections: list[TextCorrection]

class QuestionMarking(BaseModel):
    individual_questions: list[str]
    general_feedback: str
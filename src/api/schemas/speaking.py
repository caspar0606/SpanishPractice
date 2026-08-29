from pydantic import BaseModel, Field

from src.api.schemas.learn import LessonCard
from src.infrastructure.llm.contracts.text_correction import TextCorrection
from src.infrastructure.llm.contracts.writing import WritingSummary


class SpeakingGenerateRequest(BaseModel):
    username: str


class SpeakingGenerateResponse(BaseModel):
    prompt: str


class SpeakingSubmitRequest(BaseModel):
    username: str
    transcript: str


class SpeakingSubmitResponse(BaseModel):
    corrections: TextCorrection
    feedback: WritingSummary
    counted: bool = True
    not_counted_reasons: list[str] = Field(default_factory=list)
    lessons: list[LessonCard] = Field(default_factory=list)

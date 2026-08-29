from pydantic import BaseModel, Field

from src.api.schemas.learn import LessonCard
from src.infrastructure.llm.contracts.reading import ReadingGeneration, QuestionMarking, TextCorrections

class ReadingGenerationRequest(BaseModel):
    """The server rebuilds the exercise context from the stored exercise."""

    username: str

class ReadingGenerationResponse(BaseModel):
    prompt: ReadingGeneration

class ReadingUserRequest(BaseModel):
    username: str
    user_response: list[str]

class ReadingSummaryResponse(BaseModel):
    corrections: TextCorrections
    feedback: QuestionMarking
    # Whether this attempt counted towards the learner's level, and why not.
    counted: bool = True
    not_counted_reasons: list[str] = []
    lessons: list[LessonCard] = Field(default_factory=list)








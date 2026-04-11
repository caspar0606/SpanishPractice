from pydantic import BaseModel

from src.domain.models.exercise import ExerciseContext
from src.infrastructure.llm.contracts.reading import ReadingGeneration, QuestionMarking, TextCorrections

class ReadingGenerationRequest(BaseModel):
    username: str
    exercise_context: ExerciseContext

class ReadingGenerationResponse(BaseModel):
    prompt: ReadingGeneration

class ReadingUserRequest(BaseModel):
    username: str
    user_response: list[str]

class ReadingSummaryResponse(BaseModel):
    corrections: TextCorrections
    feedback: QuestionMarking








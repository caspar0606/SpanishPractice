from pydantic import BaseModel

from src.domain.models.exercise import ExerciseContext
from src.infrastructure.llm.contracts.writing import WritingSummary
from src.infrastructure.llm.contracts.text_correction import TextCorrection

class WritingGenerationRequest(BaseModel):
    username: str
    exercise_context: ExerciseContext

class WritingGenerationResponse(BaseModel):
    prompt: str

class WritingUserRequest(BaseModel):
    username: str
    prompt: str
    user_response: str

class WritingSummaryResponse(BaseModel):
    corrections: TextCorrection
    feedback: WritingSummary




from pydantic import BaseModel

from src.domain.models.exercise import Exercise, ExerciseContext
from src.infrastructure.llm.contracts.writing import WritingCorrection, WritingSummary

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
    detailed_correction: WritingCorrection
    summarised_correction: WritingSummary




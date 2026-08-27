from pydantic import BaseModel

from src.infrastructure.llm.contracts.writing import WritingSummary
from src.infrastructure.llm.contracts.text_correction import TextCorrection

class WritingGenerationRequest(BaseModel):
    """The server rebuilds the exercise context from the stored exercise."""

    username: str

class WritingGenerationResponse(BaseModel):
    prompt: str

class WritingUserRequest(BaseModel):
    username: str
    prompt: str
    user_response: str

class WritingSummaryResponse(BaseModel):
    corrections: TextCorrection
    feedback: WritingSummary




from pydantic import BaseModel

from src.infrastructure.llm.contracts.drills import MarkedDrills, Drills, UserDrillResponses

class DrillGenerationRequest(BaseModel):
    """The server rebuilds the exercise context from the stored exercise."""

    username: str

class DrillGenerationResponse(BaseModel):
    prompt: Drills

class DrillUserRequest(BaseModel):
    username: str
    user_response: UserDrillResponses

class DrillSummaryResponse(BaseModel):
    marked_drills: MarkedDrills


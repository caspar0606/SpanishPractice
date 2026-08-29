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
    # Whether this attempt counted towards the learner's level, and why not.
    counted: bool = True
    not_counted_reasons: list[str] = []


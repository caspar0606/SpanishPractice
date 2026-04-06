from pydantic import BaseModel

from src.domain.models.exercise import ExerciseContext
from src.infrastructure.llm.contracts.drills import MarkedDrills, Drills, UserDrillResponses

class DrillGenerationRequest(BaseModel):
    username: str
    exercise_context: ExerciseContext

class DrillGenerationResponse(BaseModel):
    prompt: Drills

class DrillUserRequest(BaseModel):
    username: str
    user_response: UserDrillResponses

class DrillSummaryResponse(BaseModel):
    marked_drills: MarkedDrills


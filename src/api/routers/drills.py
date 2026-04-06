from fastapi import APIRouter

from src.application.services import drills as drills_file
from src.api.schemas.drills import DrillGenerationRequest, DrillGenerationResponse, DrillSummaryResponse, DrillUserRequest

router = APIRouter()

@router.post("/generate", response_model=DrillGenerationResponse)
def generate_drills(request: DrillGenerationRequest):
    result = drills_file.generate_drills(request.username)

    return DrillGenerationResponse(
        prompt=result
    )

@router.post("/submit", response_model=DrillSummaryResponse)
def submit_drills(request: DrillUserRequest):
    result = drills_file.submit_drills(request.username, request.user_response)

    return DrillSummaryResponse(
        marked_drills=result
    )

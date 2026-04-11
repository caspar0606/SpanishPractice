from fastapi import APIRouter, HTTPException

from src.application.services import drills as drills_file
from src.api.schemas.drills import DrillGenerationRequest, DrillGenerationResponse, DrillSummaryResponse, DrillUserRequest

router = APIRouter()

@router.post("/generate", response_model=DrillGenerationResponse)
def generate_drills(request: DrillGenerationRequest):
    try:
        result = drills_file.generate_drills(request.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return DrillGenerationResponse(
        prompt=result
    )

@router.post("/submit", response_model=DrillSummaryResponse)
def submit_drills(request: DrillUserRequest):
    try:
        result = drills_file.submit_drills(request.username, request.user_response)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return DrillSummaryResponse(
        marked_drills=result
    )

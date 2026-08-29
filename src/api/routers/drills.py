from fastapi import APIRouter, HTTPException

from src.application.services import drills as drills_file
from src.application.services import learn as learn_file
from src.api.schemas.learn import LessonCard
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

    marked_drills, verdict = result

    return DrillSummaryResponse(
        marked_drills=marked_drills,
        counted=verdict.genuine,
        not_counted_reasons=verdict.reasons,
        lessons=[LessonCard(**row) for row in learn_file.related_for_user(request.username)],
    )

from fastapi import APIRouter, Depends

from src.api.deps import current_username, limited
from src.api.errors import http_from_value_error
from src.api.schemas.drills import (
    DrillGenerationRequest,
    DrillGenerationResponse,
    DrillSummaryResponse,
    DrillUserRequest,
)
from src.api.schemas.learn import LessonCard
from src.application.services import drills as drills_file
from src.application.services import learn as learn_file

router = APIRouter()


@router.post("/generate", response_model=DrillGenerationResponse)
def generate_drills(
    request: DrillGenerationRequest,
    username: str = Depends(limited("drills_generate", 20)),
):
    try:
        result = drills_file.generate_drills(username)
    except ValueError as e:
        raise http_from_value_error(e) from e

    return DrillGenerationResponse(prompt=result)


@router.post("/submit", response_model=DrillSummaryResponse)
def submit_drills(request: DrillUserRequest, username: str = Depends(current_username)):
    try:
        result = drills_file.submit_drills(username, request.user_response)
    except ValueError as e:
        raise http_from_value_error(e) from e

    marked_drills, verdict = result

    return DrillSummaryResponse(
        marked_drills=marked_drills,
        counted=verdict.genuine,
        not_counted_reasons=verdict.reasons,
        lessons=[LessonCard(**row) for row in learn_file.related_for_user(username)],
    )

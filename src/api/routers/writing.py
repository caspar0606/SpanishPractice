from fastapi import APIRouter, Depends

from src.api.deps import current_username, limited
from src.api.errors import http_from_value_error
from src.api.schemas.learn import LessonCard
from src.api.schemas.writing import (
    WritingGenerationRequest,
    WritingGenerationResponse,
    WritingSummaryResponse,
    WritingUserRequest,
)
from src.application.services import learn as learn_file
from src.application.services import writing as writing_file

router = APIRouter()


@router.post("/generate", response_model=WritingGenerationResponse)
def generate_writing_instruction(
    request: WritingGenerationRequest,
    username: str = Depends(limited("writing_generate", 20)),
):
    try:
        result = writing_file.generate_instructions(username)
    except ValueError as e:
        raise http_from_value_error(e) from e

    return WritingGenerationResponse(prompt=result)


@router.post("/submit", response_model=WritingSummaryResponse)
def submit_text(request: WritingUserRequest, username: str = Depends(current_username)):
    try:
        result = writing_file.submit_response(request.user_response, username)
    except ValueError as e:
        raise http_from_value_error(e) from e

    corrections, feedback, verdict = result

    return WritingSummaryResponse(
        corrections=corrections,
        feedback=feedback,
        counted=verdict.genuine,
        not_counted_reasons=verdict.reasons,
        lessons=[LessonCard(**row) for row in learn_file.related_for_user(username)],
    )

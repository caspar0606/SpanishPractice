from fastapi import APIRouter, Depends

from src.api.deps import current_username, limited
from src.api.errors import http_from_value_error
from src.api.schemas.learn import LessonCard
from src.api.schemas.reading import (
    ReadingGenerationRequest,
    ReadingGenerationResponse,
    ReadingSummaryResponse,
    ReadingUserRequest,
)
from src.application.services import learn as learn_file
from src.application.services import reading as reading_file

router = APIRouter()


@router.post("/generate", response_model=ReadingGenerationResponse)
def generate_reading_text(
    request: ReadingGenerationRequest,
    username: str = Depends(limited("reading_generate", 20)),
):
    try:
        result = reading_file.generate_passage(username)
    except ValueError as e:
        raise http_from_value_error(e) from e

    return ReadingGenerationResponse(prompt=result)


@router.post("/submit", response_model=ReadingSummaryResponse)
def submit_responses(request: ReadingUserRequest, username: str = Depends(current_username)):
    try:
        result = reading_file.submit_response(request.user_response, username)
    except ValueError as e:
        raise http_from_value_error(e) from e

    corrections, feedback, verdict = result

    return ReadingSummaryResponse(
        corrections=corrections,
        feedback=feedback,
        counted=verdict.genuine,
        not_counted_reasons=verdict.reasons,
        lessons=[LessonCard(**row) for row in learn_file.related_for_user(username)],
    )

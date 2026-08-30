from fastapi import APIRouter, Depends

from src.api.deps import current_username, limited
from src.api.errors import http_from_value_error
from src.api.schemas.learn import LessonCard
from src.api.schemas.listening import (
    ListeningGenerateRequest,
    ListeningGenerateResponse,
    ListeningSubmitRequest,
    ListeningSubmitResponse,
)
from src.application.services import learn as learn_file
from src.application.services import listening as listening_file

router = APIRouter()


@router.post("/generate", response_model=ListeningGenerateResponse)
def generate_listening(
    request: ListeningGenerateRequest,
    username: str = Depends(limited("listening_generate", 20)),
):
    try:
        result = listening_file.generate_clip(username)
    except ValueError as e:
        raise http_from_value_error(e) from e
    return ListeningGenerateResponse(**result)


@router.post("/submit", response_model=ListeningSubmitResponse)
def submit_listening(request: ListeningSubmitRequest, username: str = Depends(current_username)):
    try:
        feedback, verdict, transcript = listening_file.submit_response(
            username, request.answers,
        )
    except ValueError as e:
        raise http_from_value_error(e) from e
    return ListeningSubmitResponse(
        feedback=feedback,
        transcript=transcript,
        counted=verdict.genuine,
        not_counted_reasons=verdict.reasons,
        lessons=[LessonCard(**row) for row in learn_file.related_for_user(username)],
    )

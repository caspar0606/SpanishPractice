from fastapi import APIRouter, HTTPException

from src.application.services import writing as writing_file
from src.application.services import learn as learn_file
from src.api.schemas.learn import LessonCard
from src.api.schemas.writing import WritingGenerationRequest, WritingGenerationResponse, WritingSummaryResponse, WritingUserRequest

router = APIRouter()

@router.post("/generate", response_model=WritingGenerationResponse)
def generate_writing_instruction(request: WritingGenerationRequest):
    try:
        result = writing_file.generate_instructions(request.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return WritingGenerationResponse(
        prompt=result
    )

@router.post("/submit", response_model=WritingSummaryResponse)
def submit_text(request: WritingUserRequest):
    try:
        result = writing_file.submit_response(request.user_response, request.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    corrections, feedback, verdict = result

    return WritingSummaryResponse(
        corrections=corrections,
        feedback=feedback,
        counted=verdict.genuine,
        not_counted_reasons=verdict.reasons,
        lessons=[LessonCard(**row) for row in learn_file.related_for_user(request.username)],
    )


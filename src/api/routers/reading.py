from fastapi import APIRouter, HTTPException

from src.application.services import reading as reading_file
from src.api.schemas.reading import ReadingGenerationRequest, ReadingGenerationResponse, ReadingUserRequest, ReadingSummaryResponse

router = APIRouter()

@router.post("/generate", response_model=ReadingGenerationResponse)
def generate_reading_text(request: ReadingGenerationRequest):
    try:
        result = reading_file.generate_passage(request.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return ReadingGenerationResponse(
        prompt=result
    )

@router.post("/submit", response_model=ReadingSummaryResponse)
def submit_responses(request: ReadingUserRequest):
    try:
        result = reading_file.submit_response(request.user_response, request.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return ReadingSummaryResponse(
        correction = result
    )

from fastapi import APIRouter

from src.application.services import reading as reading_file
from src.api.schemas.reading import ReadingGenerationRequest, ReadingGenerationResponse, ReadingUserRequest, ReadingSummaryResponse

router = APIRouter()

@router.post("/generate", response_model=ReadingGenerationResponse)
def generate_reading_text(request: ReadingGenerationRequest):
    result = reading_file.generate_passage(request.username)

    return ReadingGenerationResponse(
        prompt=result
    )

@router.post("/submit", response_model=ReadingSummaryResponse)
def submit_responses(request: ReadingUserRequest):
    result = reading_file.submit_response(request.user_response, request.username)

    return ReadingSummaryResponse(
        correction = result
    )

from fastapi import APIRouter

from src.application.services import progress as progress_file
from src.api.schemas.progress import CurrentProgressRequest, CurrentProgressResponse, HistoricalProgressRequest, HistoricalProgressResponse


router = APIRouter()

@router.post("/generate", response_model=CurrentProgressResponse)
def return_progress(request: CurrentProgressRequest):
    result = progress_file.return_progress(request.username)

    return CurrentProgressResponse(
        progress=result
    )

from fastapi import APIRouter, HTTPException

from src.application.services import progress as progress_file
from src.api.schemas.progress import CurrentProgressRequest, CurrentProgressResponse, HistoricalProgressResponse


router = APIRouter()

@router.post("/generate", response_model=CurrentProgressResponse, deprecated=True)
def return_progress(request: CurrentProgressRequest):
    """Superseded by GET /progress/{username}. Kept so an older client keeps working."""
    try:
        result = progress_file.return_progress(request.username)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    return CurrentProgressResponse(
        progress=result
    )

@router.get("/{username}", response_model=CurrentProgressResponse)
def read_progress(username: str):
    try:
        result = progress_file.return_progress(username)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    return CurrentProgressResponse(
        progress=result
    )

@router.get("/{username}/history", response_model=HistoricalProgressResponse)
def read_progress_history(username: str):
    """Current totals plus one entry per completed exercise, oldest first."""
    try:
        progress, history = progress_file.return_progress_history(username)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    return HistoricalProgressResponse(
        progress=progress,
        progress_history=history
    )

from pydantic import BaseModel

from src.domain.models.progress import Progress, ProgressUpdates


class CurrentProgressRequest(BaseModel):
    username: str

class CurrentProgressResponse(BaseModel):
    progress: Progress

class HistoricalProgressRequest(BaseModel):
    username: str

class HistoricalProgressResponse(BaseModel):
    progress: Progress
    progress_history: list[ProgressUpdates]
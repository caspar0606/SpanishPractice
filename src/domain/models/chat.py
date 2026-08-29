"""Short chat turns stored on the user record."""

from datetime import datetime

from pydantic import BaseModel, Field


class ChatTurn(BaseModel):
    role: str
    text: str
    at: datetime = Field(default_factory=datetime.now)
    lesson_keys: list[str] = Field(default_factory=list)

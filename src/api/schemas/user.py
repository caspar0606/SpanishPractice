from pydantic import BaseModel

from src.domain.enums import OnboardingStep

class UserRequest(BaseModel):
    username: str
    key: str
    new: bool

class UserResponse(BaseModel):
    username: str
    token: str
    step: OnboardingStep

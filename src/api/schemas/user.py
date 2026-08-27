from pydantic import BaseModel

from src.domain.enums import OnboardingStep
from src.domain.models.user import User

class UserRequest(BaseModel):
    username: str
    key: str
    new: bool

class UserResponse(BaseModel):
    user: User
    step: OnboardingStep

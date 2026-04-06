from fastapi import APIRouter

from src.application import user as user_file
from src.api.schemas.user import UserRequest, UserResponse
from src.domain.models.user import User

router = APIRouter()

@router.post("/login", response_model=UserResponse)
def select_user(request: UserRequest):
    result = user_file.select_user(request.username, request.key, request.new)
    
    if not isinstance(result, User):
        raise ValueError("UserError")

    return UserResponse(
        user=result
    )
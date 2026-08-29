from fastapi import APIRouter, HTTPException

from src.api.schemas.learn import ChatAskRequest, ChatAskResponse, ChatHistoryRequest, LessonCard
from src.application.services import chat as chat_file

router = APIRouter()


@router.post("/ask", response_model=ChatAskResponse)
def chat_ask(request: ChatAskRequest):
    try:
        result = chat_file.ask(request.username, request.question)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    result["lessons"] = [LessonCard(**row) for row in result.get("lessons") or []]
    return ChatAskResponse(**result)


@router.post("/history", response_model=ChatAskResponse)
def chat_history(request: ChatHistoryRequest):
    try:
        history = chat_file.history(request.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return ChatAskResponse(answer_en="", history=history)

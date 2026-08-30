from fastapi import APIRouter, Depends, Query

from src.api.deps import limited
from src.api.errors import http_from_value_error
from src.api.schemas.translate import TranslateResponse
from src.application.services import translate as translate_file

router = APIRouter()


@router.get("/word", response_model=TranslateResponse)
def translate_word(
    q: str = Query(..., min_length=1, max_length=80),
    username: str = Depends(limited("translate", 30)),
):
    try:
        result = translate_file.lookup_word(q)
    except ValueError as e:
        raise http_from_value_error(e) from e
    return TranslateResponse(**result.model_dump())

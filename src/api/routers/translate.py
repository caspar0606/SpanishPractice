from fastapi import APIRouter, HTTPException, Query

from src.api.schemas.translate import TranslateResponse
from src.application.services import translate as translate_file

router = APIRouter()


@router.get("/word", response_model=TranslateResponse)
def translate_word(q: str = Query(..., min_length=1, max_length=80)):
    try:
        result = translate_file.lookup_word(q)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return TranslateResponse(**result.model_dump())

from fastapi import APIRouter, Depends

from src.api.deps import current_username
from src.api.errors import http_from_value_error
from src.api.schemas.vocab import (
    VocabListRequest,
    VocabListResponse,
    VocabMarkRequest,
    VocabReviewItem,
    VocabReviewResponse,
    VocabReviewSubmitRequest,
)
from src.application.services import vocab as vocab_file
from src.domain.models.vocab import VocabEntry
from src.domain.rules import vocab as vocab_rules

router = APIRouter()


@router.post("/list", response_model=VocabListResponse)
def vocab_list(request: VocabListRequest, username: str = Depends(current_username)):
    try:
        items = vocab_file.list_entries(username)
    except ValueError as e:
        raise http_from_value_error(e) from e
    return VocabListResponse(items=items, due_count=len(vocab_rules.due_entries(items)))


@router.post("/mark", response_model=VocabEntry)
def vocab_mark(request: VocabMarkRequest, username: str = Depends(current_username)):
    try:
        return vocab_file.mark(username, request.lemma, request.status, request.starred)
    except ValueError as e:
        raise http_from_value_error(e) from e


@router.post("/review", response_model=VocabReviewResponse)
def vocab_review(request: VocabListRequest, username: str = Depends(current_username)):
    try:
        due = vocab_file.due(username)
    except ValueError as e:
        raise http_from_value_error(e) from e
    return VocabReviewResponse(
        items=[VocabReviewItem(lemma=item.lemma, gloss_en=item.gloss_en) for item in due],
    )


@router.post("/review/submit")
def vocab_review_submit(request: VocabReviewSubmitRequest, username: str = Depends(current_username)):
    try:
        updated = vocab_file.record_review(
            username,
            [row.model_dump() for row in request.results],
        )
    except ValueError as e:
        raise http_from_value_error(e) from e
    return {"items": updated}

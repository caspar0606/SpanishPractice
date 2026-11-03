from fastapi import HTTPException

from src.application.exercise_selection import UNFINISHED_EXERCISE


def http_from_value_error(exc: ValueError) -> HTTPException:
    detail = str(exc)
    if detail.startswith(UNFINISHED_EXERCISE):
        return HTTPException(status_code=409, detail=detail)
    return HTTPException(status_code=400, detail=detail)

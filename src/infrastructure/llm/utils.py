import json
from pydantic import BaseModel


def serialise_for_prompt(value) -> str:
    if value is None:
        return ""

    if isinstance(value, BaseModel):
        return json.dumps(value.model_dump(), indent=2, ensure_ascii=False)

    if isinstance(value, (dict, list)):
        return json.dumps(value, indent=2, ensure_ascii=False)

    return str(value)
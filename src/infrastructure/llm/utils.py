import json
from typing import Type
from pydantic import BaseModel


def serialise_for_prompt(value) -> str:
    if value is None:
        return ""

    if isinstance(value, BaseModel):
        return json.dumps(value.model_dump(), indent=2, ensure_ascii=False)

    if isinstance(value, (dict, list)):
        return json.dumps(value, indent=2, ensure_ascii=False)

    return str(value)


def model_schema_as_json(model: Type[BaseModel]) -> str:
    """Print a Pydantic model's JSON Schema (no instance required)."""
    return json.dumps(model.model_json_schema(), indent=2, ensure_ascii=False)
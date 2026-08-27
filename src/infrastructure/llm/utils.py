import json
import types
from enum import Enum
from typing import Any, Type, get_args, get_origin

from pydantic import BaseModel

from src.domain.enums import is_category_sentinel


def _to_prompt_jsonable(value: Any) -> Any:
    """Convert nested values into something json.dumps can handle."""
    if value is None:
        return None

    if isinstance(value, BaseModel):
        return value.model_dump()

    if isinstance(value, dict):
        return {str(k): _to_prompt_jsonable(v) for k, v in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [_to_prompt_jsonable(v) for v in value]

    return value


def serialise_for_prompt(value) -> str:
    if value is None:
        return ""

    if isinstance(value, BaseModel):
        return json.dumps(value.model_dump(), indent=2, ensure_ascii=False)

    if isinstance(value, (dict, list)):
        return json.dumps(_to_prompt_jsonable(value), indent=2, ensure_ascii=False)

    return str(value)


def model_schema_as_json(model: Type[BaseModel]) -> str:
    """Print a Pydantic model's JSON Schema (no instance required)."""
    return json.dumps(model.model_json_schema(), indent=2, ensure_ascii=False)


def model_prompt_example_as_json(model: Type[BaseModel]) -> str:
    """
    Render example JSON for prompts.

    Priority:
    1) `Model.example_json()` if defined (model-owned, stays in sync with contract intent)
    2) `model_config.json_schema_extra["example"]` if present
    3) fallback placeholder example derived from field types
    """
    if hasattr(model, "example_json") and callable(getattr(model, "example_json")):
        ex = model.example_json()  # type: ignore[attr-defined]
        return json.dumps(ex, indent=2, ensure_ascii=False)

    extra = getattr(model, "model_config", {}).get("json_schema_extra", {})
    if isinstance(extra, dict) and "example" in extra:
        return json.dumps(extra["example"], indent=2, ensure_ascii=False)

    return json.dumps(_fallback_example_dict(model), indent=2, ensure_ascii=False)


def _is_sentinel_enum_member(member: Enum) -> bool:
    return is_category_sentinel(member)


def _fallback_for_annotation(annotation: Any) -> Any:
    origin = get_origin(annotation)
    args = get_args(annotation)

    # Optional[T] / Union[T, None] -> null
    if args and any(a is type(None) for a in args):  # noqa: E721
        return None

    if origin is None and isinstance(annotation, type):
        if issubclass(annotation, BaseModel):
            return _fallback_example_dict(annotation)
        if issubclass(annotation, Enum):
            for m in annotation:
                if not _is_sentinel_enum_member(m):
                    return m.value
            return next(iter(annotation)).value
        if annotation is str:
            return "string"
        if annotation is int:
            return 0
        if annotation is float:
            return 0.0
        if annotation is bool:
            return False

    if origin in {list, set, tuple} and args:
        return [_fallback_for_annotation(args[0])]

    if origin is dict and len(args) == 2:
        k_t, v_t = args
        if isinstance(k_t, type) and issubclass(k_t, Enum):
            out: dict[str, Any] = {}
            for m in k_t:
                if _is_sentinel_enum_member(m):
                    continue
                out[str(m.value)] = _fallback_for_annotation(v_t)
            return out
        return {"key": _fallback_for_annotation(v_t)}

    if str(origin).endswith("Union") and args:
        non_none = [a for a in args if a is not type(None)]
        return _fallback_for_annotation(non_none[0] if non_none else args[0])

    if origin is getattr(types, "UnionType", None) and args:
        non_none = [a for a in args if a is not type(None)]
        return _fallback_for_annotation(non_none[0] if non_none else args[0])

    return "value"


def _fallback_example_dict(model: Type[BaseModel]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for name, field in model.model_fields.items():
        out[name] = _fallback_for_annotation(field.annotation)
    return out

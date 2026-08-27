import json
import os
from pathlib import Path

from src.domain.enums import CATEGORY_SENTINEL_VALUES
from src.domain.models.user import User
from src.domain.utils import validate_username

_PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _userdata_dir() -> Path:
    raw = os.getenv("USERDATA_DIR")
    if not raw:
        return _PROJECT_ROOT / "userdata"
    path = Path(raw)
    return path if path.is_absolute() else _PROJECT_ROOT / path


USERDATA_DIR = _userdata_dir()


def _user_file(username: str) -> Path:
    return USERDATA_DIR / f"{validate_username(username)}.json"


def _drop_sentinel_keys(progress_data: object) -> None:
    if not isinstance(progress_data, dict):
        return
    for category in ("tenses", "grammar", "topics"):
        bucket = progress_data.get(category)
        if isinstance(bucket, dict):
            for sentinel in CATEGORY_SENTINEL_VALUES:
                bucket.pop(sentinel, None)


def _strip_sentinels_from_user_data(user_data: dict) -> None:
    _drop_sentinel_keys(user_data.get("progress"))
    current = user_data.get("current_exercise")
    if isinstance(current, dict):
        _drop_sentinel_keys(current.get("score"))
    for history_name in ("exercise_history", "progress_history"):
        items = user_data.get(history_name) or []
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            _drop_sentinel_keys(item.get("score"))
            _drop_sentinel_keys(item.get("new_progress"))


def save_user_state(user: User):
    user_file = _user_file(user.name)
    user_file.parent.mkdir(parents=True, exist_ok=True)
    with user_file.open("w") as f:
        json.dump(user.model_dump(mode="json"), f, indent=4)

def create_new_user_file(username: str):
    user_file = _user_file(username)
    user_file.parent.mkdir(parents=True, exist_ok=True)

    if user_file.exists():
        print(f"User '{username}' already exists.")
        return 1
    return 0

def load_user_state(username: str):
    user_file = _user_file(username)
    if not user_file.exists():
        print(f"User '{username}' not found. Please create a new user.")
        return None

    try:
        with user_file.open("r") as f:
            user_data = json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"User '{username}' data is corrupt") from exc

    if not isinstance(user_data, dict):
        raise ValueError(f"User '{username}' data is corrupt")

    user_data["exercise_history"] = user_data.get("exercise_history") or []
    user_data["progress_history"] = user_data.get("progress_history") or []
    _strip_sentinels_from_user_data(user_data)

    return User.model_validate(user_data)

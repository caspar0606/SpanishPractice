import json
import os
from pathlib import Path

from src.domain.models.user import User
from src.domain.utils import validate_username
from src.infrastructure.persistence.migrations import to_v2

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

    return User.model_validate(to_v2(user_data))

import json
import os
from pathlib import Path

from src.domain.models.user import User

USERDATA_DIR = Path(os.getenv("USERDATA_DIR", "userdata"))

def save_user_state(user: User):
    user_file = USERDATA_DIR / f"{user.name}.json"
    user_file.parent.mkdir(parents=True, exist_ok=True)
    with user_file.open("w") as f:
        json.dump(user.model_dump(mode="json"), f, indent=4)

def create_new_user_file(username: str):
    user_file = USERDATA_DIR / f"{username}.json"
    user_file.parent.mkdir(parents=True, exist_ok=True)

    if user_file.exists():
        print(f"User '{username}' already exists.")
        return 1

    user_file.touch()

def load_user_state(username: str):
    user_file = USERDATA_DIR / f"{username}.json"
    if not user_file.exists():
        print(f"User '{username}' not found. Please create a new user.")
        return None
    
    with user_file.open("r") as f:
        user_data = json.load(f)

    user_data["history"] = user_data.get("history") or []
    user_data["progress_history"] = user_data.get("progress_history") or []

    return User.model_validate(user_data)

import json
from pathlib import Path
from src.domain.classes import User

def save_user_state(user: User):
    user_data = user.model_dump()
    user_file = Path(f"userdata/{user.name}.json")
    with user_file.open("w") as f:
        json.dump(user_data, f, indent=4)

def create_new_user_file(username: str):
    user_file = Path(f"userdata/{username}.json")

    user_file.parent.mkdir(exist_ok=True)

    if user_file.exists():
        raise FileExistsError(f"User '{username}' already exists.")

    user_file.touch()

def load_user_state(username: str) -> User:
    user_file = Path(f"userdata/{username}.json")
    if not user_file.exists():
        raise FileNotFoundError(f"No data found for user '{username}'")
    
    with user_file.open("r") as f:
        user_data = json.load(f)
    
    return User.model_validate(user_data)
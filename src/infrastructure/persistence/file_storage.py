import json
import logging
import os
import re
import tempfile
from pathlib import Path

from src.domain.models.user import User

_LOG = logging.getLogger(__name__)

# Usernames become filenames, so the accepted set excludes every path separator and
# anything that could walk out of the data directory. Requiring an alphanumeric first
# character also rules out ".", ".." and names that would create hidden files.
_SAFE_USERNAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def userdata_dir() -> Path:
    return Path(os.getenv("USERDATA_DIR", "userdata"))


def user_file_path(username: str) -> Path:
    """Resolve a username to its JSON file, rejecting anything outside the data directory.

    The pattern already excludes "/", "\\" and "..", so this cannot traverse. The
    containment check below is a second line of defence in case the pattern is ever
    loosened.
    """
    if not isinstance(username, str) or not _SAFE_USERNAME.match(username):
        raise ValueError(
            "Username must be 1 to 64 characters, using only letters, digits, "
            "dot, underscore or hyphen.",
        )

    base = userdata_dir()
    candidate = base / f"{username}.json"

    if candidate.parent.resolve() != base.resolve():
        raise ValueError("Username resolves outside the user data directory.")

    return candidate


def save_user_state(user: User):
    user_file = user_file_path(user.name)
    user_file.parent.mkdir(parents=True, exist_ok=True)

    payload = json.dumps(user.model_dump(mode="json"), indent=4)

    # Write a sibling temp file and rename it into place. A crash partway through a
    # direct open("w") would leave a truncated or empty file where the user's whole
    # progress history used to be; os.replace is atomic on POSIX and Windows alike.
    handle, temp_path = tempfile.mkstemp(
        dir=user_file.parent, prefix=f".{user_file.name}.", suffix=".tmp",
    )
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, user_file)
    except BaseException:
        Path(temp_path).unlink(missing_ok=True)
        raise


def create_new_user_file(username: str):
    user_file = user_file_path(username)
    user_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        # O_EXCL fails if the file already exists. Checking exists() first and creating
        # afterwards leaves a window where two simultaneous signups both see "free".
        os.close(os.open(user_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
    except FileExistsError:
        _LOG.info("Refused to create user '%s': already exists.", username)
        return 1


def load_user_state(username: str):
    user_file = user_file_path(username)
    if not user_file.exists():
        _LOG.info("User '%s' not found.", username)
        return None

    with user_file.open("r", encoding="utf-8") as f:
        user_data = json.load(f)

    user_data["exercise_history"] = user_data.get("exercise_history") or []
    user_data["progress_history"] = user_data.get("progress_history") or []

    return User.model_validate(user_data)

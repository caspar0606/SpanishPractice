"""Forward migrations for user JSON files.

v1 files stored a user-selected difficulty and had no goals, proficiency, or
placement. They are upgraded in place on load so existing learners keep their
history.
"""

from src.domain.enums import CATEGORY_SENTINEL_VALUES, Band, ExerciseTypes, LengthPreference
from src.domain.models.user import SCHEMA_VERSION
from src.domain.rules.band import legacy_difficulty_to_band, rank, word_count_for


def _drop_sentinel_keys(progress_data: object) -> None:
    if not isinstance(progress_data, dict):
        return
    for category in ("tenses", "grammar", "topics"):
        bucket = progress_data.get(category)
        if isinstance(bucket, dict):
            for sentinel in CATEGORY_SENTINEL_VALUES:
                bucket.pop(sentinel, None)


def strip_sentinels(user_data: dict) -> None:
    """Remove the tenses/grammar/topics axis labels from every progress map."""
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


def _migrate_exercise_config(storage: object) -> Band:
    """Rewrite a v1 exercise_config in place. Returns the band it maps to."""
    band = Band.A1
    if not isinstance(storage, dict):
        return band

    config = storage.get("exercise_config")
    if not isinstance(config, dict):
        return band

    if "band" in config:
        try:
            return Band(config["band"])
        except ValueError:
            return band

    band = legacy_difficulty_to_band(config.pop("difficulty", None))
    config["band"] = band.value
    config.setdefault("length", LengthPreference.STANDARD.value)
    config.setdefault("question_count", 0)
    config.setdefault("cefr_hint", "")

    if not config.get("word_count"):
        try:
            exercise_type = ExerciseTypes(storage.get("type"))
        except ValueError:
            exercise_type = ExerciseTypes.WRITING
        config["word_count"] = word_count_for(exercise_type, band)

    return band


def to_v2(user_data: dict) -> dict:
    """Bring a user record up to the current schema version."""
    version = user_data.get("schema_version") or 1

    if version >= SCHEMA_VERSION:
        strip_sentinels(user_data)
        return user_data

    highest_band = Band.A1
    for storage in (user_data.get("current_exercise"), *(user_data.get("exercise_history") or [])):
        band = _migrate_exercise_config(storage)
        if rank(band) > rank(highest_band):
            highest_band = band

    # v1 users have no measured proficiency. Seed from the hardest difficulty
    # they were practising at, which is the only signal the old files carry.
    user_data.setdefault(
        "proficiency",
        {
            "current": highest_band.value,
            "updated_at": None,
            "genuine_attempts_at_band": 0,
            "evidence_score": 0.0,
        },
    )
    user_data.setdefault("goals", None)
    user_data.setdefault(
        "placement",
        {
            "completed": False,
            "mcq_correct": 0,
            "mcq_total": 0,
            "writing_signal": 0.0,
            "reading_signal": 0.0,
            "assigned_band": None,
            "taken_at": None,
        },
    )

    user_data["schema_version"] = SCHEMA_VERSION
    strip_sentinels(user_data)
    return user_data

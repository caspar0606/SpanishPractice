from datetime import datetime
from typing import Any

from src.application import container
from src.domain.enums import Skill, is_category_sentinel
from src.domain.models.exercise import AttemptMetrics, ExerciseStorage
from src.domain.models.progress import Progress, ProgressUpdates, SkillProgress
from src.domain.models.user import User
from src.domain.rules import genuine, proficiency as proficiency_rules
from src.domain.rules.score import add_scores, combine_scores
from src.domain.utils import initialise_progress
from src.infrastructure.config.logging import generate_id


def return_progress(username: str):
    user = load_user(username)
    return user.progress


def load_user(username: str) -> User:
    user = container.users().load(username)

    if user is None:
        raise ValueError(f"User '{username}' not found")

    return user


def _word_count(response: Any) -> int:
    if isinstance(response, str):
        return len(response.split())
    if isinstance(response, list):
        return sum(len(str(item).split()) for item in response)
    return 0


def prose_metrics(storage: ExerciseStorage, response: Any) -> AttemptMetrics:
    """Effort signals for writing and reading, where the answer is free text."""
    elapsed = (datetime.now() - storage.start_time).total_seconds()
    return AttemptMetrics(
        seconds_spent=max(0.0, elapsed),
        response_words=_word_count(response),
        target_words=storage.exercise_config.word_count,
    )


def item_metrics(storage: ExerciseStorage, answered: int, total: int) -> AttemptMetrics:
    """Effort signals for drills, where the answer is a set of items."""
    elapsed = (datetime.now() - storage.start_time).total_seconds()
    return AttemptMetrics(
        seconds_spent=max(0.0, elapsed),
        items_answered=answered,
        items_total=total,
    )


def accuracy_of(score: Progress) -> float | None:
    """Share of tagged attempts that were correct, or None if nothing was tagged.

    Tagging repeats the same stats across each focus area, which leaves the
    ratio unchanged even though the totals are inflated.
    """
    total = 0.0
    correct = 0.0
    for category in ("tenses", "grammar", "topics"):
        for key, stats in getattr(score, category).items():
            if is_category_sentinel(key):
                continue
            total += stats.total_attempts
            correct += stats.correct_attempts

    if total <= 0:
        return None

    return max(0.0, min(1.0, correct / total))


def _update_skill(
    user: User,
    skill: Skill,
    score: Progress,
    accuracy: float | None,
    is_genuine: bool,
) -> None:
    current = user.skills.get(skill) or SkillProgress(concepts=initialise_progress())

    current.total_attempts += 1
    current.last_practised = datetime.now()

    if is_genuine and accuracy is not None:
        combine_scores(current.concepts, score)
        current.rolling_accuracy = proficiency_rules.blend(
            current.rolling_accuracy,
            current.genuine_attempts,
            accuracy,
        )
        current.genuine_attempts += 1
        current.relative_level = proficiency_rules.relative_level(
            current.genuine_attempts,
            current.rolling_accuracy,
        )

    user.skills[skill] = current


def save_user_progress(
    user: User,
    response: Any,
    feedback: Any,
    score: Any,
    metrics: AttemptMetrics | None = None,
):
    """Marks a finished exercise, and banks it as progress if it was a real attempt.

    Every submission is stored and shown to the learner. Only genuine ones feed
    the progress tables, because those tables drive what we recommend next: two
    blank submissions on one topic must not make it look like a weak spot.
    """
    if user.current_exercise is None or user.current_exercise.prompt is None:
        raise ValueError(f"User current storage not found")

    if user.current_exercise.end_time is not None or user.current_exercise.user_response is not None:
        raise ValueError("Current exercise has already been submitted")

    storage = user.current_exercise
    metrics = metrics if metrics is not None else prose_metrics(storage, response)
    verdict = genuine.judge(metrics)
    accuracy = accuracy_of(score)

    # Accuracy is unavailable when nothing was tagged, so there is no evidence
    # to act on even if the learner clearly tried.
    counts_as_evidence = verdict.genuine and accuracy is not None

    storage.user_response = response
    storage.feedback = feedback
    storage.score = score
    storage.end_time = datetime.now()
    storage.metrics = metrics
    storage.genuine = counts_as_evidence

    skill = Skill(storage.type.value)
    _update_skill(user, skill, score, accuracy, counts_as_evidence)

    band_change = None
    if counts_as_evidence:
        standing = proficiency_rules.overall_standing(
            (entry.genuine_attempts, entry.rolling_accuracy) for entry in user.skills.values()
        )
        if standing is not None:
            user.proficiency = proficiency_rules.record_attempt(user.proficiency, standing)
            user.proficiency, band_change = proficiency_rules.review(user.proficiency)

    user.exercise_history.append(storage)
    user.progress_history.append(
        update_progress(user, storage, skill, accuracy, counts_as_evidence, band_change),
    )

    container.users().save(user)

    return verdict


def build_drill_progress_update(exercise_context, feedback) -> Progress:
    prog = initialise_progress()
    stats = feedback.stats
    aofs = exercise_context.areas_of_focus

    if aofs.focus_tenses:
        for tense in aofs.focus_tenses:
            if tense is not None and not is_category_sentinel(tense) and tense in prog.tenses:
                add_scores(prog.tenses[tense], stats)

    if aofs.focus_topics:
        for topic in aofs.focus_topics:
            if topic is not None and not is_category_sentinel(topic) and topic in prog.topics:
                add_scores(prog.topics[topic], stats)

    if aofs.focus_grammar:
        for grammar in aofs.focus_grammar:
            if grammar is not None and not is_category_sentinel(grammar) and grammar in prog.grammar:
                add_scores(prog.grammar[grammar], stats)

    return prog

def update_progress(
    user: User,
    exercise: ExerciseStorage,
    skill: Skill | None = None,
    accuracy: float | None = None,
    is_genuine: bool = True,
    band_change: str | None = None,
):
    if exercise.score is None:
        raise ValueError(f"Exercise {exercise.id} is invalid")

    if is_genuine:
        combine_scores(user.progress, exercise.score)

    return ProgressUpdates(
        id=generate_id(),
        exercise_id=exercise.id,
        time=datetime.now(),
        score=exercise.score.model_copy(deep=True),
        new_progress=user.progress.model_copy(deep=True),
        skill=skill,
        genuine=is_genuine,
        accuracy=accuracy,
        band=user.proficiency.current,
        band_change=band_change,
    )

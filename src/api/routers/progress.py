from fastapi import APIRouter, HTTPException

from src.api.schemas.progress import (
    BandSummary,
    ConceptRow,
    CurrentProgressRequest,
    CurrentProgressResponse,
    ProgressOverview,
    SkillRow,
)
from src.application.services import progress as progress_file
from src.domain.enums import Grammar, Skill, Tenses, Topics, tracked_members
from src.domain.models.progress import Progress
from src.domain.models.user import User
from src.domain.rules import band as band_rules
from src.domain.rules import proficiency as proficiency_rules
from src.domain.rules.labels import label_for
from src.domain.rules.score import calculate_score

router = APIRouter()


def _concept_rows(bucket: dict, enum_cls) -> list[ConceptRow]:
    """One row per tracked concept, including ones never practised."""
    rows: list[ConceptRow] = []
    for member in tracked_members(enum_cls):
        stats = bucket.get(member)
        total = float(stats.total_attempts) if stats else 0.0
        correct = float(stats.correct_attempts) if stats else 0.0
        rows.append(
            ConceptRow(
                key=member.value,
                label=label_for(member),
                total_attempts=total,
                correct_attempts=correct,
                score=calculate_score(stats) if stats else 0.0,
                practised=total > 0,
            ),
        )
    # Weakest practised concepts first; unpractised ones sink to the bottom.
    rows.sort(key=lambda row: (not row.practised, row.score))
    return rows


def _skill_rows(user: User) -> list[SkillRow]:
    rows: list[SkillRow] = []
    for skill in Skill:
        entry = user.skills.get(skill)
        if entry is None:
            continue
        rows.append(
            SkillRow(
                skill=skill,
                label=label_for(skill),
                relative_level=entry.relative_level,
                relative_label=label_for(entry.relative_level),
                genuine_attempts=entry.genuine_attempts,
                total_attempts=entry.total_attempts,
                accuracy=round(entry.rolling_accuracy * 100, 1),
                last_practised=entry.last_practised,
            ),
        )
    return rows


def build_overview(user: User, progress: Progress) -> ProgressOverview:
    band = user.proficiency.current
    return ProgressOverview(
        overall=BandSummary(
            band=band,
            gloss=band_rules.gloss(band),
            genuine_attempts_at_band=user.proficiency.genuine_attempts_at_band,
            attempts_until_review=proficiency_rules.attempts_until_review(user.proficiency),
            evidence_score=round(user.proficiency.evidence_score * 100, 1),
            target_accuracy=round(proficiency_rules.PROMOTION_ACCURACY * 100, 1),
        ),
        skills=_skill_rows(user),
        tenses=_concept_rows(progress.tenses, Tenses),
        grammar=_concept_rows(progress.grammar, Grammar),
        topics=_concept_rows(progress.topics, Topics),
        genuine_attempts=sum(entry.genuine_attempts for entry in user.skills.values()),
        total_attempts=len(user.exercise_history),
    )


@router.post("/generate", response_model=CurrentProgressResponse)
def return_progress(request: CurrentProgressRequest):
    try:
        user = progress_file.load_user(request.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return CurrentProgressResponse(
        progress=user.progress,
        overview=build_overview(user, user.progress),
    )

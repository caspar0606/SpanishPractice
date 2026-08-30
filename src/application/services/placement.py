from datetime import datetime

from src.application import container
from src.domain.enums import AgentNames, Band
from src.domain.models.llm import agent_request
from src.domain.models.profile import (
    PlacementForm,
    PlacementMcqItem,
    PlacementResult,
    PlacementSubmission,
    Proficiency,
)
from src.domain.models.user import User
from src.domain.rules import band as band_rules
from src.domain.rules.placement import assign_band
from src.infrastructure.llm.contracts.placement import PlacementAssessment
from src.infrastructure.llm.prompts.placement import PLACEMENT_PROMPT_CONFIG


def _load(username: str) -> User:
    user = container.users().load(username)
    if user is None:
        raise ValueError(f"User '{username}' not found")
    return user


def _bank() -> dict:
    return container.content().placement_bank()


def build_form() -> PlacementForm:
    """The placement test, with answers stripped out."""
    bank = _bank()

    return PlacementForm(
        mcq=[
            PlacementMcqItem(
                id=item["id"],
                band=Band(item["band"]),
                prompt=item["prompt"],
                options=list(item["options"]),
            )
            for item in bank["mcq"]
        ],
        writing_prompt_en=bank["writing"]["prompt_en"],
        writing_target_words=int(bank["writing"]["target_words"]),
        reading_passage=bank["reading"]["passage"],
        reading_questions=list(bank["reading"]["questions"]),
    )


def _score_mcq(answers: dict[str, str]) -> tuple[int, int]:
    items = _bank()["mcq"]
    correct = sum(
        1 for item in items if answers.get(item["id"], "").strip() == item["answer"]
    )
    return correct, len(items)


def _assess_samples(submission: PlacementSubmission) -> PlacementAssessment:
    bank = _bank()

    if not submission.writing_response.strip() and not any(
        answer.strip() for answer in submission.reading_answers
    ):
        return PlacementAssessment(
            writing_signal=0.0,
            reading_signal=0.0,
            notes_en="You did not submit a writing or reading sample, so we started you at the beginning.",
        )

    stimulus = {
        "writing_task_en": bank["writing"]["prompt_en"],
        "writing_response": submission.writing_response,
        "reading_passage": bank["reading"]["passage"],
        "reading_questions": bank["reading"]["questions"],
        "reading_answers": submission.reading_answers,
    }

    request = agent_request(
        name=AgentNames.PLACEMENT_ASSESSOR,
        system_prompt=PLACEMENT_PROMPT_CONFIG[AgentNames.PLACEMENT_ASSESSOR],
        schema=PlacementAssessment,
        stimulus=str(stimulus),
    )

    return container.llm().structured(request, PlacementAssessment)


def submit(username: str, submission: PlacementSubmission) -> dict:
    user = _load(username)

    if user.goals is None:
        raise ValueError("Set your goals before taking the placement test")

    if user.placement.completed:
        raise ValueError("Placement has already been completed")

    mcq_correct, mcq_total = _score_mcq(submission.mcq_answers)
    assessment = _assess_samples(submission)

    band = assign_band(
        mcq_correct=mcq_correct,
        mcq_total=mcq_total,
        writing_signal=assessment.writing_signal,
        reading_signal=assessment.reading_signal,
    )

    now = datetime.now()
    user.placement = PlacementResult(
        completed=True,
        mcq_correct=mcq_correct,
        mcq_total=mcq_total,
        writing_signal=assessment.writing_signal,
        reading_signal=assessment.reading_signal,
        assigned_band=band,
        taken_at=now,
    )
    user.proficiency = Proficiency(current=band, updated_at=now)
    user.first_time = False

    container.users().save(user)

    return {
        "assigned_band": band.value,
        "assigned_level": band_rules.display_level(band),
        "gloss": band_rules.gloss(band),
        "mcq_correct": mcq_correct,
        "mcq_total": mcq_total,
        "notes_en": assessment.notes_en,
    }

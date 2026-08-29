"""The recommender is a pure function of user state plus the curriculum."""

from datetime import datetime, timedelta

from src.application.services import recommender as service
from src.domain.enums import (
    Band,
    Direction,
    ExerciseTypes,
    Grammar,
    LengthPreference,
    RecommendationKind,
    Tenses,
    Topics,
    VocabStatus,
)
from src.domain.models.exercise import AreasOfFocus, ExerciseConfig, ExerciseStorage
from src.domain.models.progress import ComputeStats
from src.domain.models.vocab import VocabEntry
from src.domain.rules import curriculum as curriculum_rules
from src.infrastructure.persistence.json_content import JsonContentRepository


def steps():
    return curriculum_rules.parse_steps(JsonContentRepository().curriculum())


def practise(user, tense=None, grammar=None, correct=2, total=10):
    stats = ComputeStats(total_attempts=total, correct_attempts=correct)
    if tense is not None:
        user.progress.tenses[tense] = stats
    if grammar is not None:
        user.progress.grammar[grammar] = stats
    return user


def history(user, types, genuine=True):
    for index, kind in enumerate(types):
        user.exercise_history.append(
            ExerciseStorage(
                id=f"h{index}",
                type=kind,
                areas_of_focus=AreasOfFocus(),
                exercise_config=ExerciseConfig(band=Band.A2, word_count=80),
                start_time=datetime.now() - timedelta(hours=len(types) - index),
                prompt="p",
                genuine=genuine,
            ),
        )
    return user


def kinds(cards):
    return [card.kind for card in cards]


def test_a_fresh_a2_learner_gets_one_card_of_each_kind(deps, fake_users):
    user = fake_users.seed("learner", band=Band.A2)
    cards = service.cards_for(user, steps())

    assert kinds(cards) == [
        RecommendationKind.NEEDED,
        RecommendationKind.ROADMAP,
        RecommendationKind.GOAL,
    ]
    assert len(cards) == 3
    assert all(card.estimated_minutes >= 8 for card in cards)
    assert all(card.reason_en for card in cards)
    assert all(card.title_en for card in cards)


def test_needed_is_the_weakest_practised_introduced_concept(deps, fake_users):
    user = fake_users.seed("learner", band=Band.A2)
    practise(user, tense=Tenses.PRESENTE_DE_INDICATIVO, correct=9, total=10)
    practise(user, tense=Tenses.PRETERITO_IMPERFECTO, correct=2, total=10)

    cards = service.cards_for(user, steps())
    needed = cards[0]

    assert needed.kind is RecommendationKind.NEEDED
    assert needed.type is ExerciseTypes.DRILLS
    assert needed.focus.focus_tenses == [Tenses.PRETERITO_IMPERFECTO]
    assert "Past tense (used to / was doing)" in needed.title_en
    assert "20%" in needed.reason_en


def test_needed_ignores_a_weak_concept_the_band_has_not_unlocked(deps, fake_users):
    """Futuro is an A2.5 unlock, so a struggling A2 learner is not sent there."""
    user = fake_users.seed("learner", band=Band.A2)
    practise(user, tense=Tenses.PRESENTE_DE_INDICATIVO, correct=8, total=10)
    practise(user, tense=Tenses.FUTURO_SIMPLE, correct=0, total=10)

    needed = service.cards_for(user, steps())[0]
    assert needed.focus.focus_tenses == [Tenses.PRESENTE_DE_INDICATIVO]


def test_roadmap_is_the_next_named_concept_above_this_band(deps, fake_users):
    user = fake_users.seed("learner", band=Band.A2)
    roadmap = service.cards_for(user, steps())[1]

    assert roadmap.kind is RecommendationKind.ROADMAP
    assert roadmap.focus.focus_tenses == [Tenses.FUTURO_SIMPLE]
    assert "future tense" in roadmap.reason_en.lower()


def test_needed_can_be_a_grammar_point(deps, fake_users):
    user = fake_users.seed("learner", band=Band.A2)
    practise(user, tense=Tenses.PRESENTE_DE_INDICATIVO, correct=9, total=10)
    practise(user, grammar=Grammar.VERB_SUBJECT_CONJUGATION, correct=1, total=10)

    needed = service.cards_for(user, steps())[0]
    assert needed.focus.focus_grammar == [Grammar.VERB_SUBJECT_CONJUGATION]
    assert "Matching verbs to their subject" in needed.title_en


def test_goal_card_follows_the_learner_direction(deps, fake_users):
    user = fake_users.seed("learner", band=Band.A2)
    user.goals.direction = Direction.SCHOOL
    fake_users.save(user)

    goal = service.cards_for(fake_users.load("learner"), steps())[-1]
    assert goal.kind is RecommendationKind.GOAL
    assert goal.focus.focus_topics == [Topics.SCHOOL]
    assert goal.type in {
        ExerciseTypes.WRITING,
        ExerciseTypes.READING,
        ExerciseTypes.LISTENING,
        ExerciseTypes.SPEAKING,
    }
    assert "school" in goal.reason_en.lower()


def test_three_writings_in_a_row_are_not_followed_by_a_fourth(deps, fake_users):
    user = fake_users.seed("learner", band=Band.A2)
    history(user, [ExerciseTypes.WRITING, ExerciseTypes.WRITING, ExerciseTypes.WRITING])

    types = {card.type for card in service.cards_for(user, steps())}
    assert ExerciseTypes.WRITING not in types


def test_throwaway_attempts_do_not_count_toward_the_streak(deps, fake_users):
    user = fake_users.seed("learner", band=Band.A2)
    history(user, [ExerciseTypes.WRITING, ExerciseTypes.WRITING], genuine=False)
    history(user, [ExerciseTypes.READING])

    types = [card.type for card in service.cards_for(user, steps())]
    assert ExerciseTypes.WRITING in types


def test_a_b2_learner_still_gets_three_cards(deps, fake_users):
    user = fake_users.seed("learner", band=Band.B2)
    cards = service.cards_for(user, steps())
    assert len(cards) == 3
    assert cards[1].kind is RecommendationKind.ROADMAP
    assert cards[1].kind_label == "Keep practising"


def test_goal_card_prefers_the_skill_that_has_been_practised_less(deps, fake_users):
    from src.domain.enums import Skill
    from src.domain.models.progress import SkillProgress
    from src.domain.utils import initialise_progress

    user = fake_users.seed("learner", band=Band.A2)
    user.skills[Skill.WRITING] = SkillProgress(
        genuine_attempts=6, total_attempts=6, concepts=initialise_progress(),
    )
    user.skills[Skill.READING] = SkillProgress(
        genuine_attempts=1, total_attempts=1, concepts=initialise_progress(),
    )
    user.skills[Skill.LISTENING] = SkillProgress(
        genuine_attempts=5, total_attempts=5, concepts=initialise_progress(),
    )
    user.skills[Skill.SPEAKING] = SkillProgress(
        genuine_attempts=5, total_attempts=5, concepts=initialise_progress(),
    )

    goal = [card for card in service.cards_for(user, steps()) if card.kind is RecommendationKind.GOAL][0]
    assert goal.type is ExerciseTypes.READING


def test_due_vocab_becomes_the_first_card(deps, fake_users):
    user = fake_users.seed("learner", band=Band.A2)
    user.vocab = [
        VocabEntry(lemma=f"word{i}", gloss_en=f"gloss {i}", status=VocabStatus.NEW)
        for i in range(5)
    ]
    fake_users.save(user)

    cards = service.cards_for(fake_users.load("learner"), steps())
    assert cards[0].kind is RecommendationKind.VOCAB
    assert len(cards) == 3


def test_recommend_loads_the_user_and_the_shipped_curriculum(deps, fake_users):
    fake_users.seed("learner", band=Band.A1)
    cards = service.recommend("learner")
    assert len(cards) == 3
    assert cards[0].focus.focus_tenses == [Tenses.PRESENTE_DE_INDICATIVO]
    assert cards[1].focus.focus_tenses == [Tenses.PRETERITO_PERFECTO_SIMPLE]


def test_recommend_refuses_a_learner_who_has_not_placed(deps, fake_users):
    fake_users.seed("learner", band=Band.A2, placed=False)
    try:
        service.recommend("learner")
    except ValueError as exc:
        assert "placement" in str(exc).lower()
    else:
        raise AssertionError("expected placement to be required")

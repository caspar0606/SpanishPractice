"""Vocab merge, ignore, and due-for-review scheduling."""

from datetime import datetime, timedelta

from src.application.services import vocab as vocab_file
from src.domain.enums import VocabStatus
from src.domain.models.vocab import VocabEntry
from src.domain.rules import vocab as vocab_rules
from src.infrastructure.llm.contracts.learn import VocabExtraction, VocabItem


def test_harvest_merges_new_lemmas(deps, fake_users, fake_llm):
    fake_users.seed("learner")
    fake_llm.structured_responses[VocabExtraction] = VocabExtraction(
        items=[
            VocabItem(lemma="mercado", gloss_en="market", topic="travel"),
            VocabItem(lemma="hermana", gloss_en="sister"),
        ],
    )
    vocab_file.harvest("learner", "Ayer fui al mercado con mi hermana y compramos pan fresco.")
    lemmas = {entry.lemma for entry in fake_users.saved["learner"].vocab}
    assert lemmas == {"mercado", "hermana"}


def test_ignored_lemmas_are_not_due():
    now = datetime.now()
    entries = [
        VocabEntry(lemma="pan", gloss_en="bread", status=VocabStatus.NEW),
        VocabEntry(lemma="sol", gloss_en="sun", status=VocabStatus.IGNORED),
        VocabEntry(
            lemma="mar",
            gloss_en="sea",
            status=VocabStatus.LEARNING,
            next_review=now + timedelta(days=3),
        ),
    ]
    due = vocab_rules.due_entries(entries, now)
    assert [entry.lemma for entry in due] == ["pan"]


def test_mark_star_and_ignore(deps, fake_users, fake_llm):
    fake_users.seed("learner")
    fake_llm.structured_responses[VocabExtraction] = VocabExtraction(
        items=[VocabItem(lemma="tren", gloss_en="train")],
    )
    vocab_file.harvest("learner", "El tren sale a las ocho de la mañana desde Madrid.")
    vocab_file.mark("learner", "tren", starred=True)
    vocab_file.mark("learner", "tren", status=VocabStatus.IGNORED)
    entry = fake_users.saved["learner"].vocab[0]
    assert entry.starred is True
    assert entry.status is VocabStatus.IGNORED
    assert vocab_rules.due_entries(fake_users.saved["learner"].vocab) == []


def test_gloss_match_is_exact_after_normalising():
    assert vocab_rules.gloss_matches("House", "house")
    assert vocab_rules.gloss_matches("café", "cafe")
    assert not vocab_rules.gloss_matches("a", "house")
    assert not vocab_rules.gloss_matches("house", "household")
    assert not vocab_rules.gloss_matches("", "house")


def test_review_ignores_a_client_supplied_correct_flag(deps, fake_users, fake_llm):
    fake_users.seed("learner")
    fake_llm.structured_responses[VocabExtraction] = VocabExtraction(
        items=[VocabItem(lemma="pan", gloss_en="bread")],
    )
    vocab_file.harvest("learner", "Compramos pan fresco en el mercado esta mañana juntos.")
    updated = vocab_file.record_review(
        "learner",
        [{"lemma": "pan", "guess": "a", "correct": True}],
    )
    assert updated[0].times_correct == 0
    assert updated[0].status is VocabStatus.LEARNING

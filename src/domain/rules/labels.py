"""Plain-English names for the things we track.

The UI shows these instead of Spanish grammar terminology, so a learner who
does not yet know what "pretérito imperfecto" means can still read their own
progress. Served from the backend so the wording cannot drift from the enums.
"""

from enum import Enum

from src.domain.enums import Grammar, RecommendationKind, RelativeLevel, Skill, Tenses, Topics

TENSE_LABELS: dict[Tenses, str] = {
    Tenses.PRESENTE_DE_INDICATIVO: "Present tense",
    Tenses.PRETERITO_PERFECTO_SIMPLE: "Past tense (finished actions)",
    Tenses.PRETERITO_IMPERFECTO: "Past tense (used to / was doing)",
    Tenses.FUTURO_SIMPLE: "Future tense (will)",
    Tenses.CONDICIONAL_SIMPLE: "Conditional (would)",
}

GRAMMAR_LABELS: dict[Grammar, str] = {
    Grammar.GENDER_AGREEMENT: "Masculine and feminine agreement",
    Grammar.PLURALITY_AGREEMENT: "Singular and plural agreement",
    Grammar.POR_PARA_USAGE: "Choosing between por and para",
    Grammar.INDIRECT_DIRECT_PRONOUN_USAGE: "Object pronouns (me, te, lo, le)",
    Grammar.VERB_SUBJECT_CONJUGATION: "Matching verbs to their subject",
}

TOPIC_LABELS: dict[Topics, str] = {
    Topics.TRAVEL: "Travel",
    Topics.SCHOOL: "School and study",
    Topics.WORK: "Work",
    Topics.CULTURE: "Culture",
    Topics.CURRENT_EVENTS: "News and current events",
    Topics.EMOTIONS: "Feelings and opinions",
    Topics.RELATIONSHIPS: "Family and relationships",
}

SKILL_LABELS: dict[Skill, str] = {
    Skill.WRITING: "Writing",
    Skill.READING: "Reading",
    Skill.LISTENING: "Listening",
    Skill.SPEAKING: "Speaking",
    Skill.DRILLS: "Grammar drills",
}

KIND_LABELS: dict[RecommendationKind, str] = {
    RecommendationKind.NEEDED: "What you need",
    RecommendationKind.ROADMAP: "Next on the roadmap",
    RecommendationKind.GOAL: "For your goal",
    RecommendationKind.VOCAB: "Vocab review",
}

RELATIVE_LEVEL_LABELS: dict[RelativeLevel, str] = {
    RelativeLevel.BELOW: "Behind your overall level",
    RelativeLevel.AT: "In line with your overall level",
    RelativeLevel.ABOVE: "Ahead of your overall level",
}

_ALL: dict[Enum, str] = {
    **TENSE_LABELS,
    **GRAMMAR_LABELS,
    **TOPIC_LABELS,
    **SKILL_LABELS,
    **KIND_LABELS,
    **RELATIVE_LEVEL_LABELS,
}


def label_for(member: Enum) -> str:
    """Falls back to a readable form of the raw key for anything unmapped."""
    if member in _ALL:
        return _ALL[member]
    raw = getattr(member, "value", member)
    return str(raw).replace("_", " ").capitalize()

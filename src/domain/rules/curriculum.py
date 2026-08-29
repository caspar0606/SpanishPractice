"""The A1→B2 unlock order, independent of how well a learner has practised.

A concept is *introduced* once the learner's band has reached the step that
unlocks it. Practised-or-not is a separate question, answered from Progress.
"""

from src.domain.enums import Band, ConceptAxis, Grammar, Tenses
from src.domain.models.curriculum import ConceptRef, CurriculumStep
from src.domain.models.progress import Progress
from src.domain.rules.band import rank
from src.domain.rules.score import calculate_score


def parse_steps(raw: dict) -> list[CurriculumStep]:
    steps = [CurriculumStep.model_validate(step) for step in raw.get("steps", [])]
    if not steps:
        raise ValueError("Curriculum must list at least one step")
    return steps


def introduced(steps: list[CurriculumStep], band: Band) -> tuple[list[Tenses], list[Grammar]]:
    """Every concept unlocked at or below this band, in roadmap order."""
    tenses: list[Tenses] = []
    grammar: list[Grammar] = []
    seen_t: set[Tenses] = set()
    seen_g: set[Grammar] = set()
    ceiling = rank(band)
    for step in steps:
        if rank(step.band) > ceiling:
            continue
        for tense in step.tenses:
            if tense not in seen_t:
                seen_t.add(tense)
                tenses.append(tense)
        for point in step.grammar:
            if point not in seen_g:
                seen_g.add(point)
                grammar.append(point)
    return tenses, grammar


def next_unlock(steps: list[CurriculumStep], band: Band) -> ConceptRef | None:
    """The first concept sitting above the current band.

    Empty complexity-only steps are skipped, so A1's next concept is the first
    A2 tense rather than a blank A1.5 row.
    """
    ceiling = rank(band)
    for step in steps:
        if rank(step.band) <= ceiling:
            continue
        if step.tenses:
            return ConceptRef(axis=ConceptAxis.TENSE, tense=step.tenses[0])
        if step.grammar:
            return ConceptRef(axis=ConceptAxis.GRAMMAR, grammar=step.grammar[0])
    return None


def weakest_introduced(progress: Progress, tenses: list[Tenses], grammar: list[Grammar]) -> ConceptRef | None:
    """The practised introduced concept with the lowest score.

    Unpractised concepts are not 'weak' — they have never been tried. If nothing
    introduced has been practised yet, the first introduced concept is returned
    so a brand-new learner still has a Needed card.
    """
    ranked: list[tuple[float, int, ConceptRef]] = []
    order = 0
    for tense in tenses:
        stats = progress.tenses.get(tense)
        if stats is None or stats.total_attempts <= 0:
            continue
        ranked.append((calculate_score(stats), order, ConceptRef(axis=ConceptAxis.TENSE, tense=tense)))
        order += 1
    for point in grammar:
        stats = progress.grammar.get(point)
        if stats is None or stats.total_attempts <= 0:
            continue
        ranked.append((calculate_score(stats), order, ConceptRef(axis=ConceptAxis.GRAMMAR, grammar=point)))
        order += 1

    if ranked:
        ranked.sort(key=lambda item: (item[0], item[1]))
        return ranked[0][2]

    if tenses:
        return ConceptRef(axis=ConceptAxis.TENSE, tense=tenses[0])
    if grammar:
        return ConceptRef(axis=ConceptAxis.GRAMMAR, grammar=grammar[0])
    return None

from pydantic import BaseModel, Field

from src.domain.enums import Band, ConceptAxis, Grammar, Tenses


class CurriculumStep(BaseModel):
    """One half-step on the A1→B2 roadmap.

    Empty `tenses`/`grammar` lists mean this band is a complexity bump, not a
    new concept. The recommender skips those when looking for the next unlock.
    """

    band: Band
    tenses: list[Tenses] = Field(default_factory=list)
    grammar: list[Grammar] = Field(default_factory=list)


class ConceptRef(BaseModel):
    """A single tense or grammar point the roadmap can name."""

    axis: ConceptAxis
    tense: Tenses | None = None
    grammar: Grammar | None = None

    def member(self) -> Tenses | Grammar:
        if self.axis is ConceptAxis.TENSE:
            if self.tense is None:
                raise ValueError("Tense concept is missing its tense")
            return self.tense
        if self.grammar is None:
            raise ValueError("Grammar concept is missing its grammar point")
        return self.grammar

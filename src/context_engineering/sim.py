"""A deterministic responder for reproducible experiments (Chapter 0.3).

What this is: a rule-based stand-in for a language model that answers ONLY
from designated grounding components (evidence, memory, tool results) in a
bundle. It scores sentences by keyword coverage of the question, returns the
best sentence with its provenance citation, and refuses below a threshold.

What this is NOT: a model. It demonstrates mechanical context effects —
what evidence was present, what got cited, what fits — deterministically.
It cannot demonstrate attention, fluency, or positional effects; chapters
that need model behavior say so explicitly and provide optional protocols.

The refusal behavior is deliberate: an honest INSUFFICIENT CONTEXT answer
is a feature of well-engineered systems, not a failure (Chapter 0.3).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .context import ComponentKind, ContextBundle, ContextComponent

SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
WORD_RE = re.compile(r"[a-z0-9']+")

STOPWORDS = {
    "how", "many", "the", "a", "an", "is", "are", "per", "to", "of", "up",
    "do", "does", "did", "what", "when", "which", "who", "and", "or", "in",
    "on", "for", "with", "by", "at", "can", "i", "we", "you", "my", "our",
}

#: Component kinds the responder will ground answers in.
GROUNDING_KINDS = (
    ComponentKind.EVIDENCE,
    ComponentKind.MEMORY,
    ComponentKind.TOOL_RESULT,
)

INSUFFICIENT = "INSUFFICIENT CONTEXT — no evidence available to answer."


def _keywords(text: str) -> set:
    return {w for w in WORD_RE.findall(text.lower()) if w not in STOPWORDS}


def _sentences(text: str) -> list:
    return [s.strip() for s in SENTENCE_RE.split(text) if s.strip()]


@dataclass
class Answer:
    """The responder's output: text, citations, status, grounding score."""

    text: str
    citations: list = field(default_factory=list)
    status: str = "answered"  # "answered" | "insufficient_evidence"
    score: float = 0.0
    component_id: str = ""

    @property
    def grounded(self) -> bool:
        return self.status == "answered"


@dataclass
class _Candidate:
    text: str
    component_id: str
    citation: str
    score: float


class DeterministicResponder:
    """Answer questions strictly from a bundle's grounding components."""

    def __init__(self, min_coverage: float = 0.5) -> None:
        #: Minimum fraction of question keywords a sentence must cover.
        #: This is a POLICY decision (when to refuse), not a tuning knob
        #: to be lowered until refusals disappear (Chapter 0.3 exercise).
        self.min_coverage = min_coverage

    def _citation(self, comp: ContextComponent) -> str:
        if comp.source is not None:
            return comp.source.citation()
        return comp.effective_label or comp.id

    def candidates(self, question: str, bundle: ContextBundle) -> list:
        """All grounding sentences scored by keyword coverage (best first)."""
        q_words = _keywords(question)
        found: list = []
        if not q_words:
            return found
        for comp in bundle:
            if comp.kind not in GROUNDING_KINDS:
                continue
            for sentence in _sentences(comp.content):
                overlap = len(q_words & _keywords(sentence))
                score = overlap / len(q_words)
                found.append(
                    _Candidate(
                        text=sentence,
                        component_id=comp.id,
                        citation=self._citation(comp),
                        score=score,
                    )
                )
        found.sort(key=lambda c: c.score, reverse=True)
        return found

    def answer(self, question: str, bundle: ContextBundle) -> Answer:
        """Produce an Answer for ``question`` given ``bundle``."""
        ranked = self.candidates(question, bundle)
        if not ranked or ranked[0].score < self.min_coverage:
            return Answer(text=INSUFFICIENT, citations=[], status="insufficient_evidence")
        best = ranked[0]
        return Answer(
            text=best.text,
            citations=[best.citation],
            status="answered",
            score=round(best.score, 3),
            component_id=best.component_id,
        )

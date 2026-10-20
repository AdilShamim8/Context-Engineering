"""Lab 00 — The first context experiment (deterministic, offline).

Demonstrates the core thesis of the curriculum: changing the information
available to a responder changes the answer — including confident, citable,
WRONG answers built on stale evidence.

This file is deliberately self-contained (standard library only) so that it
works before the reference library is introduced in Part I. The production
version of these ideas lives in ``src/context_engineering/``.

Everything here is synthetic: Nimbus Dynamics is a fictional company.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

QUESTION = "How many remote days per week are allowed?"


@dataclass
class Document:
    """A policy document with the provenance metadata that enables citations."""

    doc_id: str
    version: str
    effective_date: str
    text: str

    @property
    def citation(self) -> str:
        return f"{self.doc_id} v{self.version} (effective {self.effective_date})"


# --- Synthetic evidence: two versions of the same fictional policy -----------

POLICY_V2 = Document(
    doc_id="hr-remote-work",
    version="2",
    effective_date="2026-08-14",
    text=(
        "Nimbus Dynamics remote work policy. Employees may work remotely up to "
        "2 days per week. Remote work requests must be approved by the direct "
        "manager. The policy applies to full-time employees in all offices."
    ),
)

POLICY_V1 = Document(  # superseded by v2 — kept only to demonstrate staleness
    doc_id="hr-remote-work",
    version="1",
    effective_date="2024-02-01",
    text=(
        "Nimbus Dynamics remote work policy. Employees may work remotely up to "
        "3 days per week. Remote work requests must be approved by the direct "
        "manager. The policy applies to full-time employees in all offices."
    ),
)

# --- A deliberately tiny rule-based responder --------------------------------

STOPWORDS = {"how", "many", "the", "a", "is", "are", "per", "to", "of", "up"}

_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
_WORD_RE = re.compile(r"[a-z0-9]+")


def _keywords(text: str) -> set[str]:
    return {w for w in _WORD_RE.findall(text.lower()) if w not in STOPWORDS}


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_RE.split(text) if s.strip()]


def respond(question: str, documents: list[Document]) -> tuple[str, str | None]:
    """Answer the question from the supplied documents only.

    Returns (answer, citation). If no sentence scores above the threshold,
    the responder refuses — an honest refusal is better than a guess.
    """
    q_words = _keywords(question)
    best_score, best_sentence, best_doc = 0.0, None, None

    for doc in documents:
        for sentence in _sentences(doc.text):
            score = len(q_words & _keywords(sentence)) / max(len(q_words), 1)
            if score > best_score:
                best_score, best_sentence, best_doc = score, sentence, doc

    if best_doc is None or best_score < 0.5:  # refusal threshold (policy, not tuning)
        return "INSUFFICIENT CONTEXT — no evidence available to answer.", None

    return best_sentence, best_doc.citation


# --- The three scenarios ------------------------------------------------------

def run_scenario(title: str, documents: list[Document]) -> None:
    print(f"=== {title} ===")
    answer, citation = respond(QUESTION, documents)
    print(f"Answer: {answer}")
    print(f"Citation: {citation if citation else '(none)'}")
    print()


if __name__ == "__main__":
    run_scenario("Scenario 1: empty context", [])
    run_scenario("Scenario 2: current policy (v2, 2026) in context", [POLICY_V2])
    run_scenario("Scenario 3: only the stale policy (v1, 2024) in context", [POLICY_V1])

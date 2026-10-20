"""Context selection: ranking candidates beyond raw retrieval scores (Chapter 11).

Retrieval similarity scores answer "what matched the query text?" —
which is not the same as "what will help the model answer well?"
This module composes several signals into a selection decision:

- normalized retrieval score (coverage of the query),
- a small recency boost (recent sources, by effective date),
- an authority weight from metadata (owner-ranked sources, optional),
- near-duplicate removal (redundancy control),
- diversity (MMR-style: skip candidates too similar to already-selected
  ones), trading a little relevance for breadth of coverage.

Honest limitation, stated in Chapter 11: these weights are heuristics.
They encode defensible defaults, not universal truths; the right way to
choose between selection policies is the evaluation harness (Chapter 27),
never intuition alone.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

from .context import ComponentKind, ContextComponent, TrustLevel
from .retrieval import RetrievedChunk

WORD_RE = re.compile(r"[a-z0-9']+")

#: Sources effective within this many days get a recency boost.
RECENCY_WINDOW_DAYS = 180
RECENCY_BONUS = 0.15


def _keywords(text: str) -> set:
    return set(WORD_RE.findall(text.lower()))


def _similarity(a: str, b: str) -> float:
    """Jaccard similarity over keyword sets — cheap near-duplicate detector."""
    ka, kb = _keywords(a), _keywords(b)
    if not ka or not kb:
        return 0.0
    return len(ka & kb) / len(ka | kb)


@dataclass
class SelectionPolicy:
    """Knobs of the selection stage. Defaults are sane, not sacred."""

    max_items: int = 8
    min_score: float = 0.0    # drop candidates whose normalized score is below this
    dedup_threshold: float = 0.7  # Jaccard >= this → near-duplicate
    diversity: bool = True   # MMR-style: skip items too similar to selected ones


def _recency_bonus(source, today: date | None) -> float:
    if source is None or not getattr(source, "effective_date", ""):
        return 0.0
    try:
        eff = date.fromisoformat(str(source.effective_date)[:10])
    except ValueError:
        return 0.0
    reference = today or date.today()
    age = (reference - eff).days
    if 0 <= age <= RECENCY_WINDOW_DAYS:
        return RECENCY_BONUS * (1.0 - age / RECENCY_WINDOW_DAYS)
    return 0.0


def rank(
    retrieved: list,
    policy: SelectionPolicy = None,
    today: date | None = None,
) -> list:
    """Composite-rank retrieved chunks and select the final evidence set.

    Steps: normalize scores → add recency/authority bonuses → dedup
    near-duplicates (keep the higher composite) → apply diversity → cap
    at ``max_items``. Returns the selected RetrievedChunks, best first.
    """
    policy = policy or SelectionPolicy()
    if not retrieved:
        return []

    today = today or date.today()
    max_score = max(r.score for r in retrieved) or 1.0

    scored: list = []
    for item in retrieved:
        normalized = item.score / max_score
        authority = 1.0
        if item.chunk is not None:
            authority = float(item.chunk.metadata.get("authority_weight", 1.0))
        composite = (normalized + _recency_bonus(item.source, today)) * authority
        scored.append((composite, item))
    scored.sort(key=lambda pair: (-pair[0], pair[1].chunk_id))

    # Near-duplicate removal (keep the higher composite).
    deduped: list = []
    for composite, item in scored:
        if any(
            _similarity(item.text, kept.chunk.text if kept.chunk else kept.text) >= policy.dedup_threshold
            for _, kept in deduped
        ):
            continue
        deduped.append((composite, item))

    # Diversity: MMR-flavored — skip candidates too similar to an already-selected one.
    selected: list = []
    for composite, item in deduped:
        if composite < policy.min_score:
            continue
        if policy.diversity and any(
            _similarity(item.text, kept.chunk.text if kept.chunk else kept.text) >= policy.dedup_threshold
            for _, kept in selected
        ):
            continue
        selected.append((composite, item))
        if len(selected) >= policy.max_items:
            break

    return [item for _, item in selected]


def to_components(selected: list, priority_start: int = 2) -> list:
    """Convert selected RetrievedChunks into UNTRUSTED EVIDENCE components.

    Rank order maps to priority (best evidence = lowest priority number).
    Trust is UNTRUSTED by default: retrieved content is data, never
    instructions (Chapter 3's rule, enforced here at the boundary).
    """
    components: list = []
    for rank_index, item in enumerate(selected):
        components.append(
            ContextComponent(
                id=item.chunk_id,
                kind=ComponentKind.EVIDENCE,
                content=item.text,
                priority=priority_start + rank_index,
                trust=TrustLevel.UNTRUSTED,
                source=item.source,
                metadata={"selection_rank": rank_index, "retrieval_score": item.score},
            )
        )
    return components

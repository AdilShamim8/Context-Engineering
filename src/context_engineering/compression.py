"""Context compression: dedup, extractive selection, structured notes
(Chapter 14).

Compression is a destructive operation performed under budget pressure.
The design principle here: **compression must preserve what the task
cannot afford to lose** — numbers, dates, identifiers, exceptions, and
provenance — before it optimizes anything else.

The extractive compressor implements that principle directly:

1. Sentences containing must-preserve patterns (numbers, dates, IDs,
   quantities) are pinned first.
2. Remaining budget goes to the highest-scoring ordinary sentences
   (early sentences and policy statements score higher).
3. Output preserves ORIGINAL sentence order — a summary that reorders
   causal or procedural text changes its meaning.

What this deliberately does NOT do: abstractive summarization (requires
a model, is nondeterministic, and can hallucinate — Chapter 14 discusses
when it is worth the risk and how to test it). This module is fully
deterministic and testable.
"""

from __future__ import annotations

import re

from .tokens import heuristic_token_count

SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")

#: Patterns whose containing sentence is pinned during compression.
MUST_PRESERVE_PATTERNS = (
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),        # ISO dates
    re.compile(r"\b\d+(?:[.,]\d+)?\b"),           # numbers (incl. decimals)
    re.compile(r"\b[A-Z]{2,}-\d{2,}\b"),          # incident/flag IDs like INC-2026-0714
    re.compile(r"\b(?:must|never|only|required|forbidden)\b", re.IGNORECASE),  # constraints
)


def _sentences(text: str) -> list:
    return [s.strip() for s in SENTENCE_RE.split(text) if s.strip()]


def _must_preserve(sentence: str) -> bool:
    return any(pattern.search(sentence) for pattern in MUST_PRESERVE_PATTERNS)


def deduplicate(texts: list, threshold: float = 0.7) -> list:
    """Remove near-duplicate texts (Jaccard over keywords), keeping order."""
    kept: list = []
    seen_sets: list = []
    for text in texts:
        words = set(re.findall(r"[a-z0-9']+", text.lower()))
        if not words:
            continue
        duplicate = False
        for existing in seen_sets:
            union = len(words | existing)
            if union and len(words & existing) / union >= threshold:
                duplicate = True
                break
        if not duplicate:
            kept.append(text)
            seen_sets.append(words)
    return kept


def extractive_compress(text: str, max_tokens: int) -> str:
    """Compress ``text`` to about ``max_tokens`` without losing pinned facts.

    Pinned sentences (numbers, dates, IDs, constraints) are included even
    when they are "boring"; if pinned sentences alone exceed the budget,
    they are included in order anyway (losing a hard fact silently is
    worse than exceeding a soft budget — the allocator, not the compressor,
    owns the hard limit; see budget.py).
    """
    if heuristic_token_count(text) <= max_tokens:
        return text

    sentences = _sentences(text)
    pinned = [s for s in sentences if _must_preserve(s)]
    ordinary = [s for s in sentences if not _must_preserve(s)]

    # Ordinary scoring: earlier sentences carry more weight (lead bias),
    # with a small bonus for medium-length, informative sentences.
    def _score(index: int, sentence: str) -> float:
        length_bonus = min(len(sentence.split()), 20) / 20.0
        return (1.0 - index / max(len(ordinary), 1)) + 0.3 * length_bonus

    chosen: set = set(pinned)
    used = sum(heuristic_token_count(s) for s in pinned)
    ranked_ordinary = sorted(
        enumerate(ordinary), key=lambda pair: -_score(pair[0], pair[1])
    )
    for _, sentence in ranked_ordinary:
        cost = heuristic_token_count(sentence)
        if used + cost > max_tokens:
            continue
        chosen.add(sentence)
        used += cost

    # Original order preserved — meaning is order-sensitive.
    return " ".join(s for s in sentences if s in chosen)


def structured_notes(items: list, max_tokens: int | None = None) -> str:
    """Turn a list of statements into deduplicated bullet notes.

    Used for rolling history summaries (Chapter 17) and agent scratch
    notes (Chapter 21): a deterministic, inspectable replacement for
    "let the model summarize everything" when determinism matters.
    """
    lines: list = []
    used = 0
    for item in deduplicate([str(i).strip() for i in items if str(i).strip()]):
        bullet = f"- {item}"
        cost = heuristic_token_count(bullet)
        if max_tokens is not None and used + cost > max_tokens:
            break
        lines.append(bullet)
        used += cost
    return "\n".join(lines)

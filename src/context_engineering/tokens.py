"""Approximate token-count estimation (Chapter 2).

Limitations (stated honestly, because this is a planning tool):

- This is NOT a tokenizer. Real tokenizers are model-specific byte-pair
  encodings; exact counts come from the provider's tokenizer for the exact
  model you call.
- The heuristic takes two widely used rules of thumb and uses the larger:
  roughly one token per four characters, and roughly 1.3 tokens per
  whitespace-delimited word (sub-word splits make words cost more than one
  token on average).
- Estimates are monotone: longer text never estimates to fewer tokens.
  That property is what makes budgeting decisions safe.

Use `heuristic_token_count` for capacity planning and allocation. Use
`make_estimator(exact=True)` when an optional real tokenizer is installed;
it degrades gracefully to the heuristic when the dependency is absent.
"""

from __future__ import annotations

import re

_WORD_RE = re.compile(r"\S+")


def heuristic_token_count(text: str) -> int:
    """Estimate the token count of ``text`` without a model-specific tokenizer.

    Combines a characters-per-token floor (~4 chars/token for English prose
    on modern tokenizers) with a words-based estimate (~1.3 tokens/word) and
    takes the larger, so both prose-heavy and structure-heavy text are
    handled conservatively. Returns 0 for empty input.
    """
    if not text:
        return 0
    by_chars = len(text) / 4.0
    by_words = len(_WORD_RE.findall(text)) * 1.3
    return max(1, int(round(max(by_chars, by_words))))


def make_estimator(exact: bool = False):
    """Return a token-estimating callable.

    With ``exact=True``, attempts to load the optional ``tiktoken`` package
    and returns an exact counter for a common modern encoding; if tiktoken
    is not installed, falls back to :func:`heuristic_token_count`. Either
    way, the returned callable maps ``str -> int``.

    Even the "exact" count is only exact for the encoding it uses: different
    models and providers tokenize differently. Verify against your actual
    provider's tokenizer before committing to hard limits.
    """
    if exact:
        try:  # optional dependency; never required by the curriculum
            import tiktoken  # type: ignore

            encoding = tiktoken.get_encoding("cl100k_base")

            def _exact(text: str) -> int:
                return len(encoding.encode(text))

            return _exact
        except Exception:
            pass  # fall through to the heuristic
    return heuristic_token_count

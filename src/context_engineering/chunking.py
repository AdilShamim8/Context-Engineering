"""Chunking strategies (Chapter 7).

Two strategies with different trade-offs:

- chunk_by_words: a sliding word window with overlap. Simple, uniform,
  predictable — but blind to structure; can cut a sentence or a policy
  clause in half.
- chunk_markdown: structure-aware splitting on headings and paragraphs,
  packing paragraphs under their heading up to a word limit. Preserves
  the semantic units a corpus actually has (sections), at the cost of
  more code and variable chunk sizes.

Teaching points encoded here (Chapter 7):

- Overlap reduces the "answer lives on the boundary" failure at the cost
  of duplicated tokens.
- Structure-aware chunking beats fixed windows when documents have
  meaningful sections; fixed windows win on uniform logs or transcripts.
- No strategy is universal: chunking policy is a per-corpus decision that
  you measure (Chapter 27), not folklore.
"""

from __future__ import annotations


def chunk_by_words(text: str, max_words: int = 200, overlap_words: int = 30) -> list:
    """Split ``text`` into overlapping word windows.

    Every chunk holds at most ``max_words``; consecutive windows advance by
    ``max_words - overlap_words`` words. Returns [] for empty input.
    """
    if max_words <= 0:
        raise ValueError("max_words must be positive")
    if overlap_words < 0 or overlap_words >= max_words:
        raise ValueError("overlap_words must be in [0, max_words)")
    words = text.split()
    if not words:
        return []
    step = max(1, max_words - overlap_words)
    chunks = []
    start = 0
    while start < len(words):
        window = words[start : start + max_words]
        chunks.append(" ".join(window))
        if start + max_words >= len(words):
            break
        start += step
    return chunks


def chunk_markdown(text: str, max_words: int = 200) -> list:
    """Structure-aware chunking: pack paragraphs under their heading.

    Returns a list of dicts: {"heading": str, "text": str, "words": int}.
    A heading change always starts a new chunk (section boundaries are
    semantic boundaries). Oversized paragraphs are hard-split with
    chunk_by_words. No paragraph is ever dropped.
    """
    sections: list = []  # (heading, paragraph)
    current_heading = ""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            current_heading = stripped.lstrip("#").strip()
            continue
        if stripped:
            sections.append((current_heading, stripped))

    chunks: list = []
    buf_heading = ""
    buf_words: list = []

    def flush():
        nonlocal buf_heading, buf_words
        if buf_words:
            chunks.append(
                {"heading": buf_heading, "text": " ".join(buf_words), "words": len(buf_words)}
            )
        buf_heading, buf_words = "", []

    for heading, paragraph in sections:
        para_words = paragraph.split()
        same_topic = heading == buf_heading
        fits = len(buf_words) + len(para_words) <= max_words
        if buf_words and (not same_topic or not fits):
            flush()
        if len(para_words) > max_words:
            # A single oversized paragraph: hard-split it.
            for piece in chunk_by_words(paragraph, max_words=max_words):
                chunks.append(
                    {"heading": heading, "text": piece, "words": len(piece.split())}
                )
            continue
        if not buf_words:
            buf_heading = heading
        buf_words.extend(para_words)
    flush()
    return chunks

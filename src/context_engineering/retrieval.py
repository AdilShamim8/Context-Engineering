"""Lexical retrieval: inverted index, BM25 scoring, filters, and RRF fusion
(Chapter 7, with extensions in Chapter 8).

Design decisions worth reading twice:

- Implemented from scratch (inverted index + BM25) so the mechanics are
  visible: document frequency, term saturation, length normalization.
  No vector database is used or needed at this corpus scale — Chapter 7
  explains when that changes.
- ``search`` accepts a ``predicate`` (a callable chunk -> bool). Access
  filtering MUST be applied through this mechanism BEFORE ranking, never
  by "hoping the model ignores" restricted results (Chapter 9).
- ``rrf_fuse`` implements Reciprocal Rank Fusion, the standard robust way
  to merge several ranked lists (e.g., lexical + semantic) without
  comparing incomparable score scales.

Limitations: BM25 is lexical — it cannot match synonyms or paraphrase
("time off" will not find "vacation"). Embedding-based retrieval fixes
that at the cost of a model dependency; the EmbeddingProvider boundary is
where an optional adapter would plug in (kept optional by design).
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field, replace
from typing import Callable, Optional

from .context import SourceRef

WORD_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list:
    return WORD_RE.findall(text.lower())


@dataclass
class Chunk:
    """A retrievable unit: text + provenance + arbitrary metadata."""

    chunk_id: str
    text: str
    source: Optional[SourceRef] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class RetrievedChunk:
    """A scored retrieval result."""

    chunk: Chunk
    score: float
    source: Optional[SourceRef] = None
    text: str = ""
    chunk_id: str = ""

    def __post_init__(self):
        if not self.source and self.chunk is not None:
            self.source = self.chunk.source
        if not self.text and self.chunk is not None:
            self.text = self.chunk.text
        if not self.chunk_id and self.chunk is not None:
            self.chunk_id = self.chunk.chunk_id


class LexicalIndex:
    """An inverted index with BM25 ranking over a fixed chunk list."""

    def __init__(self, chunks: list, k1: float = 1.5, b: float = 0.75) -> None:
        self.chunks = list(chunks)
        self.k1 = k1  # term-frequency saturation
        self.b = b    # length normalization
        self.doc_tokens: list = []
        self.doc_freq: dict = {}
        for chunk in self.chunks:
            tokens = tokenize(chunk.text)
            self.doc_tokens.append(tokens)
            for term in set(tokens):
                self.doc_freq[term] = self.doc_freq.get(term, 0) + 1
        self.n_docs = len(self.chunks)
        total = sum(len(toks) for toks in self.doc_tokens)
        self.avgdl = (total / self.n_docs) if self.n_docs else 0.0

    def _idf(self, term: str) -> float:
        df = self.doc_freq.get(term, 0)
        # BM25+ style non-negative idf
        return math.log(1.0 + (self.n_docs - df + 0.5) / (df + 0.5))

    def search(
        self,
        query: str,
        k: int = 5,
        predicate: Optional[Callable] = None,
    ) -> list:
        """Rank chunks against ``query``; return top ``k`` as RetrievedChunk.

        ``predicate`` filters candidate chunks BEFORE scoring — this is
        where access control plugs in (Chapter 9). If a predicate is given,
        chunks failing it are never scored, never ranked, never returned.
        """
        query_terms = set(tokenize(query))
        if not query_terms or self.n_docs == 0:
            return []

        candidates = [
            (i, chunk)
            for i, chunk in enumerate(self.chunks)
            if predicate is None or predicate(chunk)
        ]

        scored: list = []
        for i, chunk in candidates:
            tokens = self.doc_tokens[i]
            tf: dict = {}
            for tok in tokens:
                tf[tok] = tf.get(tok, 0) + 1
            dl = len(tokens)
            score = 0.0
            for term in query_terms:
                freq = tf.get(term, 0)
                if freq == 0:
                    continue
                idf = self._idf(term)
                norm = freq * (self.k1 + 1.0)
                denom = freq + self.k1 * (1.0 - self.b + self.b * (dl / self.avgdl if self.avgdl else 1.0))
                score += idf * (norm / denom)
            if score > 0:
                scored.append((score, i, chunk))
        scored.sort(key=lambda item: (-item[0], item[1]))
        return [RetrievedChunk(chunk=chunk, score=round(score, 4)) for score, _, chunk in scored[:k]]


def rrf_fuse(ranked_lists: list, k: int = 60, top_k: int = 5) -> list:
    """Merge several ranked lists of RetrievedChunk via Reciprocal Rank Fusion.

    Each item's fused score is the sum over lists of 1 / (k + rank + 1),
    with ``k`` typically 60. RRF needs no score normalization, which is
    exactly why it is the right default when merging, say, BM25 scores
    with cosine similarities from an optional embedding provider.
    """
    fused: dict = {}
    best: dict = {}
    for ranked in ranked_lists:
        for rank, item in enumerate(ranked):
            key = item.chunk_id or item.text
            fused[key] = fused.get(key, 0.0) + 1.0 / (k + rank + 1)
            if key not in best or item.score > best[key].score:
                best[key] = item
    ordered = sorted(fused.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
    return [replace(best[key], score=round(score, 4)) for key, score in ordered]

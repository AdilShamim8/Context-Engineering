"""Tests for lexical retrieval: BM25 index, filtering, and RRF fusion."""

import unittest

from context_engineering.context import SourceRef
from context_engineering.retrieval import Chunk, LexicalIndex, RetrievedChunk, rrf_fuse


def make_chunks():
    return [
        Chunk(
            chunk_id="remote-v2",
            text="Employees may work remotely up to 2 days per week with manager approval.",
            source=SourceRef(source_id="hr-remote-work", version="2", access="internal"),
        ),
        Chunk(
            chunk_id="vacation",
            text="Employees receive 25 days of paid vacation per year.",
            source=SourceRef(source_id="hr-vacation", version="3", access="internal"),
        ),
        Chunk(
            chunk_id="compensation",
            text="Salary bands for engineering levels are set annually.",
            source=SourceRef(
                source_id="hr-compensation-bands", version="6", access="restricted:hr-confidential"
            ),
        ),
    ]


class TestLexicalIndex(unittest.TestCase):
    def setUp(self):
        self.index = LexicalIndex(make_chunks())

    def test_finds_matching_chunk(self):
        results = self.index.search("How many remote days per week are allowed?")
        self.assertTrue(results)
        self.assertEqual(results[0].chunk_id, "remote-v2")
        self.assertGreater(results[0].score, 0)

    def test_k_limits_results(self):
        results = self.index.search("employees", k=1)
        self.assertEqual(len(results), 1)

    def test_exact_term_matches(self):
        # Lexical retrieval is EXACT-token: "remotely" matches, but a query
        # for "remote" would not (no stemming) — a teaching point of Ch. 7/8.
        results = self.index.search("remotely")
        self.assertTrue(results)
        self.assertEqual(results[0].chunk_id, "remote-v2")

    def test_no_match_returns_empty(self):
        self.assertEqual(self.index.search("quantum entanglement"), [])

    def test_predicate_excludes_before_ranking(self):
        # Simulate access control: internal users must never see restricted chunks.
        results = self.index.search(
            "salary bands engineering levels",
            k=5,
            predicate=lambda chunk: not chunk.source.access.startswith("restricted"),
        )
        ids = [r.chunk_id for r in results]
        self.assertNotIn("compensation", ids)

    def test_predicate_keeps_restricted_when_allowed(self):
        results = self.index.search(
            "salary bands engineering levels",
            k=5,
            predicate=lambda chunk: chunk.source.access.startswith("restricted"),
        )
        self.assertEqual([r.chunk_id for r in results], ["compensation"])


class TestRRFFusion(unittest.TestCase):
    def test_item_in_both_lists_ranks_first(self):
        a = [Retrieved("x", 9.0), Retrieved("shared", 8.0)]
        b = [Retrieved("shared", 0.2), Retrieved("y", 0.1)]
        fused = rrf_fuse([a, b], top_k=3)
        self.assertEqual(fused[0].chunk_id, "shared")

    def test_fused_score_present(self):
        a = [Retrieved("x", 1.0), Retrieved("y", 0.5)]
        fused = rrf_fuse([a], top_k=2)
        self.assertEqual(fused[0].chunk_id, "x")
        self.assertGreater(fused[0].score, fused[1].score)


def Retrieved(chunk_id, score):
    """Build a real RetrievedChunk for fusion tests (rrf_fuse needs dataclasses)."""
    chunk = Chunk(chunk_id=chunk_id, text=f"text-{chunk_id}")
    return RetrievedChunk(chunk=chunk, score=score)


if __name__ == "__main__":
    unittest.main()

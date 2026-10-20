"""Tests for selection: composite ranking, dedup, diversity, components."""

import unittest
from datetime import date

from context_engineering.context import ComponentKind, SourceRef, TrustLevel
from context_engineering.retrieval import Chunk, RetrievedChunk
from context_engineering.selection import SelectionPolicy, rank, to_components

TODAY = date(2026, 10, 20)


def hit(chunk_id, text, score, version="1", effective="2026-01-01", access="internal"):
    source = SourceRef(
        source_id=chunk_id.split("-")[0],
        version=version,
        effective_date=effective,
        access=access,
    )
    chunk = Chunk(chunk_id=chunk_id, text=text, source=source)
    return RetrievedChunk(chunk=chunk, score=score)


class TestRank(unittest.TestCase):
    def test_empty_input(self):
        self.assertEqual(rank([]), [])

    def test_caps_at_max_items(self):
        hits = [hit(f"c{i}", f"unique content number {i}", 1.0) for i in range(20)]
        self.assertEqual(len(rank(hits, SelectionPolicy(max_items=5))), 5)

    def test_dedup_removes_near_duplicates(self):
        hits = [
            hit("a", "Employees may work remotely up to 2 days per week with approval.", 5.0),
            hit("b", "Employees may work remotely up to 2 days per week with approval.", 4.9),
            hit("c", "The vacation policy allows 25 days of paid leave.", 3.0),
        ]
        ranked = rank(hits, SelectionPolicy(dedup_threshold=0.6))
        ids = [r.chunk_id for r in ranked]
        self.assertEqual(ids.count("a") + ids.count("b"), 1)
        self.assertIn("c", ids)

    def test_recency_bonus_can_flip_order(self):
        # Recency is a TIEBREAKER (bonus maxes at 0.15), not a dominator:
        # it flips near-equal scores, not large gaps — by design (Ch. 11).
        old = hit("old", "Remote work policy statement about weekly allowances.", 3.2, effective="2023-01-01")
        new = hit("new", "Remote work policy statement about weekly allowances.", 3.0, effective="2026-10-01")
        ranked = rank([old, new], today=TODAY)
        # Same text → dedup keeps only the higher composite (the fresh one).
        self.assertEqual(len(ranked), 1)
        self.assertEqual(ranked[0].chunk_id, "new")

    def test_min_score_filters(self):
        hits = [
            hit("strong", "remote work policy weekly days", 10.0),
            hit("weak", "remote work policy weekly days", 0.1),
        ]
        ranked = rank(hits, SelectionPolicy(min_score=0.5, dedup_threshold=0.99))
        ids = [r.chunk_id for r in ranked]
        self.assertIn("strong", ids)
        self.assertNotIn("weak", ids)

    def test_authority_weight_applies(self):
        hits = [
            hit("wiki", "Remote work rules summary restating the policy.", 5.0),
            hit("official", "Remote work rules summary restating the policy.", 4.0),
        ]
        for h, weight in zip(hits, (0.5, 2.0)):
            h.chunk.metadata["authority_weight"] = weight
        ranked = rank(hits, today=TODAY)  # dedup will keep the official one
        self.assertEqual(ranked[0].chunk_id, "official")


class TestToComponents(unittest.TestCase):
    def test_components_are_untrusted_evidence(self):
        ranked = rank([hit("a", "Two remote days per week are allowed.", 5.0)], today=TODAY)
        components = to_components(ranked)
        self.assertEqual(len(components), 1)
        comp = components[0]
        self.assertEqual(comp.kind, ComponentKind.EVIDENCE)
        self.assertEqual(comp.trust, TrustLevel.UNTRUSTED)
        self.assertEqual(comp.source.version, "1")
        self.assertEqual(comp.metadata["selection_rank"], 0)

    def test_priority_ascending_by_rank(self):
        hits = [hit(f"c{i}", f"distinct content {i} alpha beta gamma", 5.0 - i) for i in range(3)]
        components = to_components(rank(hits, today=TODAY))
        priorities = [c.priority for c in components]
        self.assertEqual(priorities, sorted(priorities))


if __name__ == "__main__":
    unittest.main()

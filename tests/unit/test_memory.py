"""Tests for the memory store: conflicts, TTL, access, audit, persistence."""

import unittest
from datetime import date

from context_engineering.memory import MemoryRecord, MemoryStore
from context_engineering.provenance import AccessPolicy


def record(rid, content, kind="fact", ttl_days=None, access="internal", source="user-stated"):
    return MemoryRecord(record_id=rid, content=content, kind=kind, ttl_days=ttl_days, access=access, source=source)


class TestUpsertAndConflicts(unittest.TestCase):
    def test_insert_and_replace_audited(self):
        store = MemoryStore()
        store.upsert(record("r1", "User's team is Platform Reliability."))
        result = store.upsert(record("r1", "User's team is Data Platform."))
        self.assertTrue(result["replaced"])
        ops = [entry["op"] for entry in store.audit]
        self.assertEqual(ops, ["insert", "replace"])

    def test_numeric_conflict_flagged_not_hidden(self):
        store = MemoryStore()
        store.upsert(record("r1", "The stipend is 300 dollars per quarter."))
        result = store.upsert(record("r2", "The stipend is 150 dollars per quarter."))
        self.assertEqual(len(result["conflicts"]), 1)
        self.assertEqual(result["conflicts"][0]["reason"], "numeric_mismatch")

    def test_overlapping_content_conflict(self):
        store = MemoryStore()
        store.upsert(record("r1", "User prefers morning meetings on mondays"))
        result = store.upsert(record("r2", "User prefers morning meetings on tuesdays"))
        self.assertTrue(result["conflicts"])
        self.assertEqual(result["conflicts"][0]["reason"], "overlapping_content_differs")

    def test_unrelated_records_do_not_conflict(self):
        store = MemoryStore()
        store.upsert(record("r1", "Team picnic happens in July."))
        result = store.upsert(record("r2", "Deployment rollback uses feature flags."))
        self.assertEqual(result["conflicts"], [])

    def test_bad_kind_rejected(self):
        with self.assertRaises(ValueError):
            MemoryRecord(record_id="x", content="y", kind="vibe")


class TestRetrieval(unittest.TestCase):
    def test_retrieval_ranks_relevant_first(self):
        store = MemoryStore()
        store.upsert(record("r1", "User's team is Platform Reliability."))
        store.upsert(record("r2", "Vacation carryover cap is 5 days."))
        hits = store.retrieve("What is the user's team?", k=2)
        self.assertEqual(hits[0].record_id, "r1")

    def test_access_policy_filters_before_scoring(self):
        store = MemoryStore()
        store.upsert(record("public-note", "Company all-hands is monthly.", access="public"))
        store.upsert(record("private-note", "User's performance rating discussion.", access="restricted:hr-confidential"))
        policy = AccessPolicy.from_levels("public", "internal")
        hits = store.retrieve("performance rating discussion", k=5, access_policy=policy)
        self.assertEqual([r.record_id for r in hits], [])
        hits = store.retrieve("company all-hands", k=5, access_policy=policy)
        self.assertEqual([r.record_id for r in hits], ["public-note"])

    def test_expired_records_invisible(self):
        store = MemoryStore()
        old = record("old", "The incident bridge number is 555.", ttl_days=7)
        # Force an old creation date to make it expired.
        old.created_at = "2020-01-01T00:00:00+00:00"
        old.updated_at = old.created_at
        store.upsert(old)
        self.assertEqual(store.retrieve("incident bridge number"), [])
        purged = store.purge_expired(today=date(2026, 10, 20))
        self.assertEqual(purged, ["old"])
        self.assertIn("purge_expired", [e["op"] for e in store.audit])


class TestDeletionAndPersistence(unittest.TestCase):
    def test_delete_audited_with_reason(self):
        store = MemoryStore()
        store.upsert(record("r1", "Something the user asked to forget."))
        store.delete("r1", reason="user deletion request (Chapter 25)")
        self.assertEqual(len(store.records), 0)
        self.assertEqual(store.audit[-1]["reason"], "user deletion request (Chapter 25)")

    def test_delete_all(self):
        store = MemoryStore()
        store.upsert(record("a", "one"))
        store.upsert(record("b", "two"))
        count = store.delete_all(reason="end of engagement")
        self.assertEqual(count, 2)
        self.assertEqual(len(store.audit), 3)  # insert, insert, delete_all

    def test_state_round_trip(self):
        store = MemoryStore()
        store.upsert(record("r1", "User prefers concise answers.", kind="preference"))
        store.upsert(record("r2", "Sprint review moved to Thursday."))
        store.delete("r2", reason="test")
        restored = MemoryStore.from_state(store.to_state())
        self.assertIn("r1", restored.records)
        self.assertEqual(len(restored.audit), len(store.audit))


if __name__ == "__main__":
    unittest.main()

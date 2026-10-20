"""Tests for provenance: access policy, freshness, version selection."""

import unittest
from datetime import date

from context_engineering.context import SourceRef
from context_engineering.provenance import (
    ACCESS_UNKNOWN,
    AccessPolicy,
    FreshnessPolicy,
    group_by_source,
    select_current_versions,
)
from context_engineering.retrieval import Chunk

TODAY = date(2026, 10, 20)


def chunk_with_access(chunk_id, access):
    return Chunk(
        chunk_id=chunk_id,
        text="some content",
        source=SourceRef(source_id=chunk_id, access=access, effective_date="2026-01-01"),
    )


class TestAccessPolicy(unittest.TestCase):
    def setUp(self):
        self.policy = AccessPolicy.from_levels("public", "internal")
        self.chunks = [
            chunk_with_access("internal-doc", "internal"),
            chunk_with_access("restricted-doc", "restricted:security-team"),
            chunk_with_access("other-restricted", "restricted:hr-confidential"),
        ]

    def test_filters_restricted(self):
        kept = [c.chunk_id for c in self.policy.filter(self.chunks)]
        self.assertEqual(kept, ["internal-doc"])

    def test_fails_closed_on_unknown_access(self):
        no_source = Chunk(chunk_id="mystery", text="content with no source", source=None)
        kept = self.policy.filter(self.chunks + [no_source])
        self.assertNotIn("mystery", [c.chunk_id for c in kept])
        self.assertEqual(_access(no_source), ACCESS_UNKNOWN)

    def test_restricted_visible_to_authorized_policy(self):
        security_policy = AccessPolicy.from_levels("public", "internal", "restricted:security-team")
        kept = [c.chunk_id for c in security_policy.filter(self.chunks)]
        self.assertIn("restricted-doc", kept)
        self.assertNotIn("other-restricted", kept)


def _access(chunk):
    from context_engineering.provenance import _access_of

    return _access_of(chunk)


class TestFreshnessPolicy(unittest.TestCase):
    def _source(self, effective):
        return SourceRef(source_id="doc", version="1", effective_date=effective)

    def test_recent_source_ok(self):
        policy = FreshnessPolicy(max_age_days=180, on_stale="exclude")
        verdict = policy.verdict(self._source("2026-09-01"), today=TODAY)
        self.assertTrue(verdict.ok)
        self.assertFalse(verdict.stale)

    def test_old_source_excluded(self):
        policy = FreshnessPolicy(max_age_days=180, on_stale="exclude")
        verdict = policy.verdict(self._source("2025-06-01"), today=TODAY)
        self.assertFalse(verdict.ok)
        self.assertTrue(verdict.stale)
        self.assertIn("days old", verdict.reason)

    def test_old_source_labeled_but_kept(self):
        policy = FreshnessPolicy(max_age_days=180, on_stale="label")
        verdict = policy.verdict(self._source("2025-06-01"), today=TODAY)
        self.assertTrue(verdict.ok)
        self.assertTrue(verdict.stale)

    def test_missing_date_is_reported_not_crashed(self):
        policy = FreshnessPolicy(max_age_days=180)
        verdict = policy.verdict(SourceRef(source_id="doc"), today=TODAY)
        self.assertTrue(verdict.ok)
        self.assertIn("no effective date", verdict.reason)

    def test_rejects_bad_action(self):
        with self.assertRaises(ValueError):
            FreshnessPolicy(on_stale="explode")


class TestVersionSelection(unittest.TestCase):
    def _v(self, sid, version, effective):
        return SourceRef(source_id=sid, version=version, effective_date=effective)

    def test_newest_numeric_version_wins(self):
        current = select_current_versions(
            [self._v("policy", "1", "2024-02-01"), self._v("policy", "2", "2026-08-14")]
        )
        self.assertEqual(len(current), 1)
        self.assertEqual(current[0].version, "2")

    def test_effective_date_breaks_version_ties(self):
        # Two version-1 drafts: the later effective date is "current".
        current = select_current_versions(
            [self._v("doc", "1", "2026-01-01"), self._v("doc", "1", "2026-06-01")]
        )
        self.assertEqual(current[0].effective_date, "2026-06-01")

    def test_group_by_source_groups_all_versions(self):
        grouped = group_by_source(
            [self._v("policy", "1", "2024-02-01"), self._v("policy", "2", "2026-08-14")]
        )
        self.assertEqual(len(grouped["policy"]), 2)


if __name__ == "__main__":
    unittest.main()

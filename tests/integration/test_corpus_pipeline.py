"""Integration tests: the synthetic corpus loads, chunks, and retrieves correctly.

These tests run against the real Nimbus Dynamics corpus in
datasets/synthetic/corpus and pin the governance behaviors that later parts
depend on: versioned policies, access-restricted documents, and the
synthetic injection fixture.
"""

import os
import unittest

from context_engineering.corpus import default_corpus_dir, load_chunks, load_corpus
from context_engineering.provenance import select_current_versions
from context_engineering.retrieval import LexicalIndex

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CORPUS_DIR = os.path.join(REPO_ROOT, "datasets", "synthetic", "corpus")


class TestCorpusIntegrity(unittest.TestCase):
    def test_manifest_and_files_agree(self):
        docs = load_corpus(CORPUS_DIR)
        self.assertGreaterEqual(len(docs), 12)
        for doc in docs:
            self.assertTrue(doc.text.strip(), f"{doc.doc_id} is empty")
            self.assertTrue(doc.source.effective_date, f"{doc.doc_id} has no effective date")

    def test_every_document_has_owner_and_access(self):
        for doc in load_corpus(CORPUS_DIR):
            self.assertTrue(doc.source.owner, f"{doc.doc_id} has no owner")
            self.assertTrue(doc.source.access, f"{doc.doc_id} has no access level")


class TestCorpusRetrieval(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chunks = load_chunks(CORPUS_DIR)
        cls.index = LexicalIndex(cls.chunks)

    def test_versioned_policy_returns_current_version_first(self):
        results = self.index.search("How many remote days per week are allowed?", k=3)
        self.assertTrue(results)
        # v2 (2 days) must outrank v1 (3 days) for this query
        self.assertIn("2", results[0].text)

    def test_restricted_never_ranked_for_internal_predicate(self):
        results = self.index.search(
            "compensation bands salary engineering levels",
            k=10,
            predicate=lambda c: not c.source.access.startswith("restricted"),
        )
        for r in results:
            self.assertFalse(r.source.access.startswith("restricted"))

    def test_restricted_retrievable_when_authorized(self):
        results = self.index.search(
            "security incident report",
            k=5,
            predicate=lambda c: c.source.access.startswith("restricted:security-team"),
        )
        self.assertTrue(results)
        self.assertTrue(all("restricted:security-team" == r.source.access for r in results))

    def test_injection_fixture_present_and_flagged(self):
        # The manifest flag is document-level; exactly one chunk carries the
        # actual payload text. Both layers matter to the Part VI pipeline.
        flagged = [c for c in self.chunks if c.metadata.get("synthetic_injection")]
        self.assertGreaterEqual(len(flagged), 1)
        carrying = [c for c in self.chunks if "SYSTEM OVERRIDE" in c.text]
        self.assertEqual(len(carrying), 1)

    def test_version_selection_removes_superseded(self):
        docs = load_corpus(CORPUS_DIR)
        current = select_current_versions([d.source for d in docs])
        remote = [s for s in current if s.source_id == "hr-remote-work"]
        self.assertEqual(len(remote), 1)
        self.assertEqual(remote[0].version, "2")


if __name__ == "__main__":
    unittest.main()

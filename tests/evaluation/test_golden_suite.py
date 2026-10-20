"""Evaluation suite over the golden cases: the full pipeline under test.

The system under test here is the complete deterministic chain:
corpus → current-version filter → access-filtered retrieval → composite
selection → assembly → deterministic responder.

This is deliberately NOT the capstone app (Chapters 34–35 build that);
it is the harness's demonstration that the golden suite is independent
of the system under test and pins the curriculum's end-to-end behaviors:
version conflict resolution, access control (refusal vs. authorized
answer), no-evidence refusal, and injection-fixture non-participation.
"""

import os
import unittest

from context_engineering.assembly import assemble
from context_engineering.context import ContextBundle
from context_engineering.corpus import load_chunks
from context_engineering.evaluation import load_cases, run_suite
from context_engineering.provenance import AccessPolicy, select_current_versions
from context_engineering.retrieval import LexicalIndex
from context_engineering.selection import rank, to_components
from context_engineering.sim import DeterministicResponder
from context_engineering.tokens import heuristic_token_count

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CORPUS_DIR = os.path.join(REPO_ROOT, "datasets", "synthetic", "corpus")
GOLDEN_PATH = os.path.join(REPO_ROOT, "datasets", "synthetic", "golden", "golden_cases.json")

_responder = DeterministicResponder(min_coverage=0.5)


def current_chunks():
    """Load corpus chunks for CURRENT document versions only (Chapter 9)."""
    from context_engineering.corpus import load_corpus

    docs = load_corpus(CORPUS_DIR)
    current_sources = {
        (s.source_id, s.version) for s in select_current_versions([d.source for d in docs])
    }
    chunks = [
        c for c in load_chunks(CORPUS_DIR)
        if (c.source.source_id, c.source.version) in current_sources
    ]
    return chunks


_INDEX = LexicalIndex(current_chunks())


def pipeline_under_test(case):
    """The deterministic answer pipeline. Contract: answer_text, citations, tokens."""
    policy = AccessPolicy.from_levels(*case.access_levels)
    hits = _INDEX.search(case.question, k=8, predicate=policy.as_predicate())
    selected = rank(hits)
    components = to_components(selected)
    bundle = ContextBundle()
    for component in components:
        bundle.add(component)
    answer = _responder.answer(case.question, bundle)
    assembled = assemble(components)
    return {
        "answer_text": answer.text,
        "citations": answer.citations,
        "tokens": assembled.tokens,
    }


class TestGoldenSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = load_cases(GOLDEN_PATH)
        cls.report = run_suite(cls.cases, pipeline_under_test)

    def test_suite_exists_and_covers_expected_behaviors(self):
        ids = [c.case_id for c in self.cases]
        self.assertGreaterEqual(len(ids), 12)
        # Conflict, access-control, refusal, and authorization behaviors present:
        self.assertTrue(any("refuses" in cid for cid in ids))
        self.assertTrue(any("answered-for-security" in cid for cid in ids))

    def test_full_suite_passes(self):
        failures = "\n".join(r.render() for r in self.report.failures())
        self.assertEqual(self.report.passed_count, self.report.total, msg=failures)

    def test_stale_version_never_wins_the_conflict_case(self):
        conflict = next(c for c in self.cases if c.case_id == "gc-01-remote-days")
        result = pipeline_under_test(conflict)
        self.assertIn("2 days", result["answer_text"])
        self.assertNotIn("3 days", result["answer_text"])

    def test_restricted_questions_refuse_and_authorized_answer(self):
        internal_case = next(c for c in self.cases if c.case_id == "gc-07-incident-refuses-for-internal")
        security_case = next(c for c in self.cases if c.case_id == "gc-09-incident-answered-for-security")
        internal_result = pipeline_under_test(internal_case)
        security_result = pipeline_under_test(security_case)
        self.assertIn("INSUFFICIENT", internal_result["answer_text"].upper())
        self.assertIn("file-share", security_result["answer_text"])

    def test_tokens_are_counted(self):
        self.assertGreater(self.report.total_tokens, 0)


if __name__ == "__main__":
    unittest.main()

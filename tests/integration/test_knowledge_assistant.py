"""Capstone integration tests: the knowledge assistant end to end."""

import os
import unittest

from context_engineering.apps.knowledge_assistant import (
    answer_question,
    golden_case_pipeline,
)
from context_engineering.budget import ContextBudget
from context_engineering.corpus import default_corpus_dir
from context_engineering.evaluation import load_cases, run_suite
from context_engineering.security import has_high_severity

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CORPUS_DIR = os.path.join(REPO_ROOT, "datasets", "synthetic", "corpus")
GOLDEN_PATH = os.path.join(REPO_ROOT, "datasets", "synthetic", "golden", "golden_cases.json")


class TestKnowledgeAssistant(unittest.TestCase):
    def test_answers_with_citation_and_full_trace(self):
        result = answer_question(
            "How many remote days per week are allowed?", corpus_dir=CORPUS_DIR
        )
        self.assertEqual(result.answer.status, "answered")
        self.assertIn("2 days", result.answer.text)
        self.assertEqual(result.citations, ["hr-remote-work v2 (2026-08-14)"])
        stages = [e.stage for e in result.trace.events]
        self.assertEqual(
            stages, ["retrieve", "screen", "select", "budget", "assemble", "respond"]
        )
        self.assertGreater(result.assembled.tokens, 0)
        self.assertGreater(result.allocation.total_allocated, 0)

    def test_restricted_content_never_assembled_for_general_users(self):
        result = answer_question(
            "What are the salary bands for engineering level 3?",
            access_levels=("public", "internal"),
            corpus_dir=CORPUS_DIR,
        )
        self.assertEqual(result.answer.status, "insufficient_evidence")
        self.assertNotIn("88,000", result.assembled.text)
        self.assertNotIn("compensation", result.assembled.text.lower())

    def test_authorized_security_user_gets_the_incident_answer(self):
        result = answer_question(
            "Which service had the path validation vulnerability?",
            access_levels=("public", "internal", "restricted:security-team"),
            corpus_dir=CORPUS_DIR,
        )
        self.assertEqual(result.answer.status, "answered")
        self.assertIn("file-share", result.answer.text)
        self.assertIn("security-incident-report", result.citations[0])

    def test_stale_version_is_structurally_unreachable(self):
        result = answer_question(
            "How many remote days per week are allowed?", corpus_dir=CORPUS_DIR
        )
        self.assertNotIn("3 days", result.assembled.text)

    def test_injection_fixture_wrapped_and_flagged_by_default(self):
        result = answer_question(
            "When does a refund need team-lead approval?", corpus_dir=CORPUS_DIR
        )
        # The refunds answer must still work; the fixture (in the same doc)
        # is labeled and delimited if present.
        self.assertIn("100", result.answer.text)
        self.assertIn("<<<UNTRUSTED", result.assembled.text)
        self.assertTrue(any("UNTRUSTED" in line for line in result.assembled.text.splitlines()))

    def test_blocking_policy_drops_high_severity_chunks(self):
        result = answer_question(
            "Tell me about SYSTEM OVERRIDE administrative mode",
            corpus_dir=CORPUS_DIR,
            screening_policy="block",
        )
        screen_event = result.trace.events_for("screen")[0]
        self.assertGreaterEqual(screen_event.notes.get("blocked", 0), 1)
        # Under block policy the payload chunk may not appear at all.
        if screen_event.notes.get("blocked", 0):
            self.assertNotIn("SYSTEM OVERRIDE", result.assembled.text)

    def test_tight_budget_degrades_gracefully(self):
        tight = ContextBudget(total_tokens=900, reserved_output_tokens=256)
        result = answer_question(
            "How many remote days per week are allowed?",
            corpus_dir=CORPUS_DIR,
            budget=tight,
        )
        self.assertLessEqual(result.allocation.total_allocated, tight.available_for_context)
        # Refusal or answer — either is acceptable degradation; crash is not.
        self.assertIn(result.answer.status, ("answered", "insufficient_evidence"))

    def test_summary_renders(self):
        result = answer_question(
            "What is the quarterly wellness stipend?", corpus_dir=CORPUS_DIR
        )
        self.assertIn("300", result.summary())


class TestCapstoneAgainstGoldenSuite(unittest.TestCase):
    """The same harness, now pointed at the capstone app (Ch. 28's promise)."""

    def test_full_golden_suite_through_the_app(self):
        cases = load_cases(GOLDEN_PATH)
        report = run_suite(cases, golden_case_pipeline)
        failures = "\n".join(r.render() for r in report.failures())
        self.assertEqual(report.passed_count, report.total, msg=failures)

    def test_trace_tokens_counted_for_suite(self):
        cases = load_cases(GOLDEN_PATH)
        report = run_suite(cases, golden_case_pipeline)
        self.assertGreater(report.total_tokens, 0)


if __name__ == "__main__":
    unittest.main()

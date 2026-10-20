"""Evaluation harness unit tests: case scoring, report rendering, ablation."""

import unittest

from context_engineering.evaluation import (
    GoldenCase,
    SuiteReport,
    ablate,
    evaluate_answer,
    run_suite,
)


def case(**kwargs):
    base = dict(
        case_id="c1",
        question="How many remote days?",
        required_facts=["2 days"],
        forbidden_facts=[],
        expected_sources=["hr-remote-work"],
        should_refuse=False,
    )
    base.update(kwargs)
    return GoldenCase(**base)


class TestEvaluateAnswer(unittest.TestCase):
    def test_correct_answer_passes(self):
        result = evaluate_answer(
            "Employees may work remotely up to 2 days per week.",
            ["hr-remote-work v2 (2026-08-14)"],
            case(),
        )
        self.assertTrue(result.passed)
        self.assertEqual(result.failures, [])

    def test_missing_fact_named_in_failure(self):
        result = evaluate_answer("Some other text entirely.", ["hr-remote-work v2"], case())
        self.assertFalse(result.passed)
        self.assertTrue(any("2 days" in f for f in result.failures))

    def test_missing_citation_named(self):
        result = evaluate_answer("Up to 2 days per week is allowed.", ["other-doc v1"], case())
        self.assertFalse(result.passed)
        self.assertTrue(any("hr-remote-work" in f for f in result.failures))

    def test_forbidden_content_fails(self):
        result = evaluate_answer(
            "Up to 3 days per week.", ["hr-remote-work v1"],
            case(forbidden_facts=["3 days"], required_facts=["2 days"]),
        )
        self.assertFalse(result.passed)
        self.assertTrue(any("forbidden" in f for f in result.failures))

    def test_refusal_required_but_answered(self):
        result = evaluate_answer("The incident was about a file share.", [], case(should_refuse=True))
        self.assertFalse(result.passed)
        self.assertTrue(any("refusal" in f for f in result.failures))

    def test_correct_refusal_passes(self):
        result = evaluate_answer(
            "INSUFFICIENT CONTEXT — no evidence available to answer.", [], case(should_refuse=True)
        )
        self.assertTrue(result.passed)

    def test_unexpected_refusal_fails_with_named_reason(self):
        result = evaluate_answer(
            "INSUFFICIENT CONTEXT — no evidence available to answer.", [], case()
        )
        self.assertFalse(result.passed)
        self.assertTrue(any("refused" in f for f in result.failures))


class TestSuiteReport(unittest.TestCase):
    def test_aggregation_and_render(self):
        cases = [case(), case(case_id="c2", should_refuse=True)]
        report = run_suite(
            cases,
            lambda c: {
                "answer_text": "Up to 2 days." if c.case_id == "c1" else "INSUFFICIENT CONTEXT",
                "citations": ["hr-remote-work v2"],
                "tokens": 42,
            },
        )
        self.assertEqual(report.total, 2)
        self.assertEqual(report.passed_count, 2)
        self.assertEqual(report.total_tokens, 84)
        rendered = report.render()
        self.assertIn("2/2 passed", rendered)
        self.assertIn("c1", rendered)

    def test_failure_report_lists_cases_and_guidance(self):
        report = run_suite([case()], lambda c: {"answer_text": "wrong", "citations": []})
        rendered = report.render()
        self.assertIn("0/1 passed", rendered)
        self.assertIn("c1", rendered)
        self.assertIn("Interpretation guidance", rendered)


class TestAblation(unittest.TestCase):
    def test_ablation_reports_all_variants(self):
        cases = [case()]
        baseline = lambda c: {"answer_text": "2 days allowed.", "citations": ["hr-remote-work v2"]}
        broken = lambda c: {"answer_text": "3 days allowed.", "citations": ["hr-remote-work v1"]}
        reports = ablate(cases, baseline, {"stale-versions": broken})
        self.assertEqual(set(reports), {"baseline", "stale-versions"})
        self.assertTrue(reports["baseline"].results[0].passed)
        self.assertFalse(reports["stale-versions"].results[0].passed)


if __name__ == "__main__":
    unittest.main()

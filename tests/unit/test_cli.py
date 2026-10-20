"""Tests for the CLI: budget explorer and context inspector."""

import io
import os
import unittest
from contextlib import redirect_stdout

from context_engineering.cli import main

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BUNDLE = os.path.join(REPO_ROOT, "datasets", "synthetic", "demo_bundle.json")


class TestBudgetCommand(unittest.TestCase):
    def test_default_budget_runs_and_reports(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["budget", "--bundle", BUNDLE])
        out = buffer.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("ev-remote-v2", out)          # evidence component appears
        self.assertIn("Summary:", out)
        self.assertIn("tool-result-calendar", out)  # every candidate rendered

    def test_tight_budget_drops_and_truncates(self):
        # 1150 total -> 510 available: the 157-token tool result gets truncated,
        # consuming the rest, and the low-priority stale evidence is dropped.
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["budget", "--total", "1150", "--bundle", BUNDLE])
        out = buffer.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("truncated", out)
        self.assertIn("dropped", out)

    def test_impossible_budget_errors_cleanly(self):
        # Window too small for the instructions themselves: BudgetError path.
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["budget", "--total", "150", "--bundle", BUNDLE])
        self.assertEqual(code, 1)  # clean, explained failure — not a traceback


class TestInspectCommand(unittest.TestCase):
    def test_inspect_prints_components_and_request(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["inspect", "--bundle", BUNDLE])
        out = buffer.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("=== COMPONENTS ===", out)
        self.assertIn("=== ASSEMBLED REQUEST", out)
        self.assertIn("<<<UNTRUSTED", out)           # untrusted delimiters visible
        self.assertIn("[instruction | trusted]", out)

    def test_inspect_with_span_markers(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["inspect", "--bundle", BUNDLE, "--mark-spans"])
        out = buffer.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("<--", out)


if __name__ == "__main__":
    unittest.main()

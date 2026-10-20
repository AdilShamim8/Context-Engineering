"""Tests for budgeting and allocation (Chapter 12)."""

import unittest

from context_engineering.budget import (
    BudgetError,
    ContextBudget,
    allocate,
)
from context_engineering.context import ComponentKind, ContextComponent

from tests.unit.test_context import make_component


class TestContextBudget(unittest.TestCase):
    def test_available_subtracts_reserved_and_margin(self):
        budget = ContextBudget(total_tokens=1000, reserved_output_tokens=200, safety_margin_tokens=50)
        self.assertEqual(budget.available_for_context, 750)

    def test_available_never_negative(self):
        budget = ContextBudget(total_tokens=100, reserved_output_tokens=200)
        self.assertEqual(budget.available_for_context, 0)


class TestAllocate(unittest.TestCase):
    def _components(self):
        return [
            ContextComponent(
                id="instructions",
                kind=ComponentKind.INSTRUCTION,
                content="Answer only from evidence. Cite sources.",
                priority=0,
            ),
            ContextComponent(
                id="evidence-a",
                kind=ComponentKind.EVIDENCE,
                content="Policy says two remote days per week are allowed. " * 3,
                priority=1,
            ),
            ContextComponent(
                id="tool-def-b",
                kind=ComponentKind.TOOL_DEFINITION,
                content="Check the team calendar for availability before booking. " * 20,
                priority=4,
            ),
        ]

    def test_all_fit_when_budget_generous(self):
        result = allocate(self._components(), ContextBudget(total_tokens=8192))
        self.assertEqual(len(result.selected), 3)
        self.assertEqual(result.total_allocated, sum(c.token_count() for c in self._components()))
        self.assertEqual(result.dropped_ids, [])

    def test_priority_decides_who_survives_tight_budget(self):
        # Tight enough that the low-priority tool definition cannot fit.
        budget = ContextBudget(total_tokens=400, reserved_output_tokens=100, safety_margin_tokens=50)
        result = allocate(self._components(), budget)
        included_ids = [c.id for c in result.selected]
        self.assertIn("instructions", included_ids)
        self.assertIn("evidence-a", included_ids)
        self.assertNotIn("tool-def-b", included_ids)  # non-truncatable, too big → dropped
        self.assertIn("tool-def-b", result.dropped_ids)

    def test_dropped_record_has_reason(self):
        budget = ContextBudget(total_tokens=400, reserved_output_tokens=100, safety_margin_tokens=50)
        result = allocate(self._components(), budget)
        dropped = [r for r in result.records if r.action == "dropped"]
        self.assertTrue(dropped)
        self.assertTrue(all("insufficient budget" in r.reason for r in dropped))

    def test_truncatable_kind_gets_truncated_not_dropped(self):
        big = ContextComponent(
            id="big-evidence",
            kind=ComponentKind.EVIDENCE,
            content="word " * 400,  # ~520 tokens
            priority=3,
        )
        budget = ContextBudget(total_tokens=400, reserved_output_tokens=100, safety_margin_tokens=50)
        result = allocate([big], budget)
        self.assertEqual(len(result.selected), 1)
        rec = result.records[0]
        self.assertEqual(rec.action, "truncated")
        self.assertLess(rec.tokens_included, rec.tokens_original)
        self.assertIn("[truncated", result.selected[0].content)
        self.assertLessEqual(result.total_allocated, budget.available_for_context)

    def test_instructions_too_big_raises(self):
        huge_instruction = ContextComponent(
            id="huge-instr",
            kind=ComponentKind.INSTRUCTION,
            content="do " * 2000,  # far exceeds the budget below
            priority=0,
        )
        with self.assertRaises(BudgetError):
            allocate([huge_instruction], ContextBudget(total_tokens=1000))

    def test_reserved_output_respected(self):
        comps = [
            ContextComponent(id="e", kind=ComponentKind.EVIDENCE, content="data " * 300, priority=1),
        ]
        budget = ContextBudget(total_tokens=1000, reserved_output_tokens=400, safety_margin_tokens=100)
        result = allocate(comps, budget)
        self.assertLessEqual(result.total_allocated, budget.available_for_context)

    def test_report_renders_every_candidate(self):
        result = allocate(self._components(), ContextBudget(total_tokens=300, reserved_output_tokens=100))
        report = result.report()
        for cid in ("instructions", "evidence-a", "tool-def-b"):
            self.assertIn(cid, report)


if __name__ == "__main__":
    unittest.main()

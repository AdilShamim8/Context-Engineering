"""Tests for the deterministic responder (Chapter 0.3)."""

import unittest

from context_engineering.context import (
    ComponentKind,
    ContextBundle,
    ContextComponent,
    SourceRef,
)
from context_engineering.sim import Answer, DeterministicResponder


def evidence_bundle():
    bundle = ContextBundle()
    bundle.add(
        ContextComponent(
            id="instruction",
            kind=ComponentKind.INSTRUCTION,
            content="Employees may work remotely up to 9 days per week.",  # decoy
            priority=0,
        )
    )
    bundle.add(
        ContextComponent(
            id="policy-chunk",
            kind=ComponentKind.EVIDENCE,
            content=(
                "Nimbus Dynamics remote work policy. Employees may work remotely "
                "up to 2 days per week. Requests must be approved by the manager."
            ),
            priority=1,
            source=SourceRef(
                source_id="hr-remote-work",
                version="2",
                effective_date="2026-08-14",
                access="internal",
            ),
        )
    )
    return bundle


class TestDeterministicResponder(unittest.TestCase):
    def setUp(self):
        self.responder = DeterministicResponder()

    def test_answers_from_evidence_with_citation(self):
        answer = self.responder.answer("How many remote days per week are allowed?", evidence_bundle())
        self.assertTrue(answer.grounded)
        self.assertEqual(answer.status, "answered")
        self.assertIn("2 days per week", answer.text)
        self.assertEqual(answer.citations, ["hr-remote-work v2 (2026-08-14)"])

    def test_never_answers_from_instruction_components(self):
        # The instruction component contains the decoy '9 days' sentence.
        answer = self.responder.answer("How many remote days per week are allowed?", evidence_bundle())
        self.assertIn("2 days", answer.text)
        self.assertNotIn("9 days", answer.text)
        self.assertNotEqual(answer.component_id, "instruction")

    def test_refuses_without_evidence(self):
        answer = self.responder.answer("How many remote days per week are allowed?", ContextBundle())
        self.assertEqual(answer.status, "insufficient_evidence")
        self.assertEqual(answer.citations, [])
        self.assertFalse(answer.grounded)

    def test_refuses_on_unrelated_question(self):
        answer = self.responder.answer("What is the company travel reimbursement rate?", evidence_bundle())
        self.assertEqual(answer.status, "insufficient_evidence")

    def test_picks_best_scoring_sentence(self):
        ranked = self.responder.candidates("How many remote days per week are allowed?", evidence_bundle())
        self.assertTrue(ranked)
        self.assertGreaterEqual(ranked[0].score, ranked[-1].score)
        self.assertEqual(ranked[0].component_id, "policy-chunk")

    def test_answer_dataclass_defaults(self):
        a = Answer(text="x")
        self.assertEqual(a.status, "answered")
        self.assertEqual(a.citations, [])
        self.assertTrue(a.grounded)


if __name__ == "__main__":
    unittest.main()

"""Tests for ordering and labeled rendering (Chapters 13, 24)."""

import unittest

from context_engineering.assembly import (
    OrderingStrategy,
    assemble,
    order_components,
    render_component,
)
from context_engineering.context import ComponentKind, ContextComponent, SourceRef, TrustLevel


def sample_components():
    return [
        ContextComponent(
            id="ev-2",
            kind=ComponentKind.EVIDENCE,
            content="Second evidence.",
            priority=2,
            trust=TrustLevel.UNTRUSTED,
            source=SourceRef(source_id="doc-b", version="1"),
        ),
        ContextComponent(
            id="instr",
            kind=ComponentKind.INSTRUCTION,
            content="Answer only from evidence.",
            priority=0,
            trust=TrustLevel.TRUSTED,
        ),
        ContextComponent(
            id="ev-1",
            kind=ComponentKind.EVIDENCE,
            content="First evidence.",
            priority=1,
            trust=TrustLevel.UNTRUSTED,
            source=SourceRef(source_id="doc-a"),
        ),
        ContextComponent(
            id="user",
            kind=ComponentKind.USER_INPUT,
            content="How many remote days?",
            priority=0,
            trust=TrustLevel.NEUTRAL,
        ),
    ]


class TestOrdering(unittest.TestCase):
    def test_kind_grouped_puts_instructions_first(self):
        ordered = order_components(sample_components(), OrderingStrategy.KIND_GROUPED)
        self.assertEqual(ordered[0].kind, ComponentKind.INSTRUCTION)
        # evidence kinds come after user input in KIND_ORDER
        kinds = [c.kind for c in ordered]
        self.assertLess(kinds.index(ComponentKind.USER_INPUT), kinds.index(ComponentKind.EVIDENCE))

    def test_priority_order_sorts_by_priority(self):
        ordered = order_components(sample_components(), OrderingStrategy.PRIORITY_ORDER)
        priorities = [c.priority for c in ordered]
        self.assertEqual(priorities, sorted(priorities))

    def test_stable_returns_input_order(self):
        comps = sample_components()
        ordered = order_components(comps, OrderingStrategy.STABLE)
        self.assertEqual([c.id for c in ordered], [c.id for c in comps])


class TestRenderComponent(unittest.TestCase):
    def test_untrusted_content_is_delimited(self):
        comp = ContextComponent(
            id="ev",
            kind=ComponentKind.EVIDENCE,
            content="RETRIEVED DATA",
            trust=TrustLevel.UNTRUSTED,
            source=SourceRef(source_id="doc-a", version="2", effective_date="2026-01-01"),
        )
        rendered = render_component(comp)
        self.assertIn("<<<UNTRUSTED", rendered)
        self.assertIn(">>>", rendered)
        self.assertIn("[evidence | untrusted]", rendered)
        self.assertIn("doc-a v2 (2026-01-01)", rendered)

    def test_trusted_content_has_no_untrusted_markers(self):
        comp = ContextComponent(
            id="instr",
            kind=ComponentKind.INSTRUCTION,
            content="Do the task.",
            trust=TrustLevel.TRUSTED,
        )
        rendered = render_component(comp)
        self.assertIn("[instruction | trusted]", rendered)
        self.assertNotIn("<<<UNTRUSTED", rendered)


class TestAssemble(unittest.TestCase):
    def test_spans_map_back_to_component_text(self):
        assembled = assemble(sample_components())
        for comp in assembled.components:
            rendered_in_text = assembled.component_text(comp.id)
            self.assertIn(comp.content, rendered_in_text)

    def test_header_appears_first(self):
        assembled = assemble(sample_components(), header="=== REQUEST ===")
        self.assertTrue(assembled.text.startswith("=== REQUEST ==="))

    def test_tokens_positive(self):
        assembled = assemble(sample_components())
        self.assertGreater(assembled.tokens, 0)

    def test_every_component_present(self):
        assembled = assemble(sample_components())
        for comp in sample_components():
            self.assertIn(comp.content, assembled.text)


if __name__ == "__main__":
    unittest.main()

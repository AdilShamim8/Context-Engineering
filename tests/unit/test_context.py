"""Tests for the component model (Chapter 3)."""

import unittest

from context_engineering.context import (
    ComponentKind,
    ContextBundle,
    ContextComponent,
    SourceRef,
    TrustLevel,
)


def make_component(cid="c1", kind=ComponentKind.EVIDENCE, content="Some content here.", **kw):
    return ContextComponent(id=cid, kind=kind, content=content, **kw)


class TestSourceRef(unittest.TestCase):
    def test_defaults(self):
        ref = SourceRef(source_id="hr-remote-work")
        self.assertEqual(ref.access, "public")
        self.assertEqual(ref.citation(), "hr-remote-work")

    def test_citation_includes_version_and_date(self):
        ref = SourceRef(source_id="hr-remote-work", version="2", effective_date="2026-08-14")
        self.assertEqual(ref.citation(), "hr-remote-work v2 (2026-08-14)")


class TestContextComponent(unittest.TestCase):
    def test_token_count_positive_and_cached(self):
        comp = make_component(content="Employees may work remotely up to two days per week.")
        first = comp.token_count()
        self.assertGreater(first, 0)
        self.assertEqual(comp.token_count(), first)  # cached, consistent

    def test_with_content_resets_token_cache(self):
        comp = make_component(content="x " * 50)
        before = comp.token_count()
        shorter = comp.with_content("tiny")
        self.assertEqual(shorter.id, comp.id)
        self.assertNotEqual(shorter.token_count(), before)
        self.assertLess(shorter.token_count(), before)

    def test_default_trust_is_neutral(self):
        self.assertEqual(make_component().trust, TrustLevel.NEUTRAL)


class TestContextBundle(unittest.TestCase):
    def test_add_chain_and_len(self):
        bundle = ContextBundle()
        bundle.add(make_component("a")).add(make_component("b"))
        self.assertEqual(len(bundle), 2)

    def test_total_tokens_sums(self):
        bundle = ContextBundle()
        bundle.add(make_component("a", content="x " * 10))
        bundle.add(make_component("b", content="y " * 20))
        self.assertEqual(
            bundle.total_tokens(),
            bundle.find("a").token_count() + bundle.find("b").token_count(),
        )

    def test_by_kind_groups(self):
        bundle = ContextBundle()
        bundle.add(make_component("a", kind=ComponentKind.EVIDENCE))
        bundle.add(make_component("b", kind=ComponentKind.EVIDENCE))
        bundle.add(make_component("c", kind=ComponentKind.INSTRUCTION))
        grouped = bundle.by_kind()
        self.assertEqual(len(grouped[ComponentKind.EVIDENCE]), 2)
        self.assertEqual(len(grouped[ComponentKind.INSTRUCTION]), 1)

    def test_find_missing_returns_none(self):
        self.assertIsNone(ContextBundle().find("nope"))


if __name__ == "__main__":
    unittest.main()

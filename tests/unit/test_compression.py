"""Tests for compression: pinned facts, dedup, structured notes."""

import unittest

from context_engineering.compression import (
    deduplicate,
    extractive_compress,
    structured_notes,
)

POLICY = (
    "Employees receive 25 days of paid vacation per year. "
    "Vacation requests must be booked at least 2 weeks in advance. "
    "Team outings are fun and morale is important and culture matters a lot. "
    "The company picnic happens every summer in the park with games. "
    "Up to 5 unused days may carry over until January 31. "
    "Morale activities include quizzes and friendly competitions occasionally."
)

NUMBERS_SENTENCE = "The stipend is 300 dollars per quarter for wellness activities."


class TestDeduplicate(unittest.TestCase):
    def test_near_duplicates_removed(self):
        texts = [
            "Employees may work remotely up to 2 days per week.",
            "Employees may work remotely up to 2 days per week.",
            "Vacation accrues monthly at a fixed rate.",
        ]
        deduped = deduplicate(texts, threshold=0.8)
        self.assertEqual(len(deduped), 2)

    def test_order_preserved(self):
        texts = ["first item about alpha", "second item about beta", "first item about alpha"]
        deduped = deduplicate(texts)
        self.assertEqual(deduped[0], "first item about alpha")
        self.assertEqual(deduped[-1], "second item about beta")


class TestExtractiveCompress(unittest.TestCase):
    def test_noop_when_already_small(self):
        self.assertEqual(extractive_compress("short text", 100), "short text")

    def test_numbers_survive_aggressive_compression(self):
        text = "The policy is generally friendly. " * 5 + NUMBERS_SENTENCE + " More filler sentences about nothing. " * 5
        compressed = extractive_compress(text, max_tokens=25)
        self.assertIn("300", compressed)

    def test_constraints_survive(self):
        text = (
            "Welcome to the team and have a wonderful onboarding experience. " * 4
            + "Employees must complete security training before production access. "
            + "Enjoy your first week with your onboarding buddy. " * 3
        )
        compressed = extractive_compress(text, max_tokens=30)
        self.assertIn("must complete security training", compressed)

    def test_output_is_not_longer_than_input(self):
        compressed = extractive_compress(POLICY, max_tokens=100000)
        self.assertLessEqual(len(compressed), len(POLICY))

    def test_preserves_sentence_order(self):
        text = (
            "First: the allowance is 25 days. "
            "Second: some ordinary filler sentence. "
            "Third: carryover allows 5 days."
        )
        compressed = extractive_compress(text, max_tokens=40)
        first_pos = compressed.find("25 days")
        third_pos = compressed.find("5 days")
        self.assertLess(first_pos, third_pos)


class TestStructuredNotes(unittest.TestCase):
    def test_bullets_and_dedup(self):
        notes = structured_notes(
            ["User prefers morning meetings.", "User prefers morning meetings.", "Team is Platform-Reliability."]
        )
        self.assertEqual(len(notes.splitlines()), 2)
        self.assertTrue(notes.startswith("- "))

    def test_budget_respected(self):
        items = [f"note number {i} with a few words" for i in range(50)]
        notes = structured_notes(items, max_tokens=40)
        from context_engineering.tokens import heuristic_token_count

        self.assertLessEqual(heuristic_token_count(notes), 40)


if __name__ == "__main__":
    unittest.main()

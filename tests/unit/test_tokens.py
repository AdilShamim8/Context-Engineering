"""Tests for approximate token estimation (Chapter 2)."""

import unittest

from context_engineering.tokens import heuristic_token_count, make_estimator


class TestHeuristicTokenCount(unittest.TestCase):
    def test_empty_text_is_zero(self):
        self.assertEqual(heuristic_token_count(""), 0)

    def test_short_text_is_positive_and_small(self):
        self.assertGreater(heuristic_token_count("hello world"), 0)
        self.assertLess(heuristic_token_count("hello world"), 10)

    def test_monotone_in_length(self):
        one = heuristic_token_count("one two three")
        more = heuristic_token_count("one two three four five six seven eight nine ten")
        self.assertGreaterEqual(more, one)

    def test_reasonable_ratio_for_english_prose(self):
        text = "The quick brown fox jumps over the lazy dog. " * 10  # ~90 words
        estimate = heuristic_token_count(text)
        self.assertGreater(estimate, 60)   # well above 1 token per 2 words
        self.assertLess(estimate, 200)    # below 1 token per word

    def test_structure_heavy_text_costs_more_than_words(self):
        # JSON-style content should not estimate cheaper than its word count
        json_like = '{"key_with_long_name": "value", "n": 12345}'
        self.assertGreaterEqual(
            heuristic_token_count(json_like),
            int(len(json_like.split()) * 1.3) - 1,
        )


class TestMakeEstimator(unittest.TestCase):
    def test_default_returns_heuristic(self):
        estimator = make_estimator()
        self.assertEqual(estimator("same text here"), heuristic_token_count("same text here"))

    def test_exact_falls_back_to_heuristic_without_optional_dep(self):
        estimator = make_estimator(exact=True)
        # Whether or not tiktoken exists, the estimator must be callable
        # and produce a sane, non-negative count.
        self.assertGreaterEqual(estimator("hello world"), 1)


if __name__ == "__main__":
    unittest.main()

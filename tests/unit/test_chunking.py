"""Tests for chunking strategies (Chapter 7)."""

import unittest

from context_engineering.chunking import chunk_by_words, chunk_markdown

SAMPLE = (
    "Remote work policy. Employees may work remotely up to two days per week. "
    "Requests must be approved by the manager. "
) * 5  # 40 words

MD_SAMPLE = """# Remote Work

## Days
Employees may work remotely up to two days per week. Requests must be approved.

## Equipment
The company provides a laptop. Monitors are extra.
"""


class TestChunkByWords(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(chunk_by_words(""), [])

    def test_respects_max_words(self):
        for chunk in chunk_by_words(SAMPLE, max_words=10, overlap_words=2):
            self.assertLessEqual(len(chunk.split()), 10)

    def test_no_words_lost(self):
        # With overlap, joined text repeats words; what must hold is that the
        # original word sequence survives as a subsequence, in order.
        words = SAMPLE.split()
        chunks = chunk_by_words(SAMPLE, max_words=20, overlap_words=5)
        joined_iter = iter(" ".join(chunks).split())
        self.assertTrue(all(w in joined_iter for w in words))

    def test_overlap_creates_repetition(self):
        hundred_words = ("w " * 100).strip()
        chunks = chunk_by_words(hundred_words, max_words=20, overlap_words=5)
        total = sum(len(c.split()) for c in chunks)
        self.assertGreater(total, 100)

    def test_rejects_bad_params(self):
        with self.assertRaises(ValueError):
            chunk_by_words(SAMPLE, max_words=0)
        with self.assertRaises(ValueError):
            chunk_by_words(SAMPLE, max_words=10, overlap_words=10)


class TestChunkMarkdown(unittest.TestCase):
    def test_heading_starts_new_chunk(self):
        chunks = chunk_markdown(MD_SAMPLE)
        headings = [c["heading"] for c in chunks]
        self.assertIn("Days", headings)
        self.assertIn("Equipment", headings)
        # No chunk mixes the two sections
        for chunk in chunks:
            if "Equipment" == chunk["heading"]:
                self.assertNotIn("two days", chunk["text"])

    def test_no_paragraph_lost(self):
        chunks = chunk_markdown(MD_SAMPLE)
        all_words = " ".join(c["text"] for c in chunks).split()
        for paragraph in ("Employees may work remotely up to two days per week.",
                          "The company provides a laptop."):
            self.assertTrue(all(w in all_words for w in paragraph.split()))

    def test_respects_word_limit(self):
        long_paragraph = ("Employees may work remotely up to two days per week. " * 20)
        chunks = chunk_markdown(f"# Section\n{long_paragraph}", max_words=50)
        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            self.assertLessEqual(chunk["words"], 50)

    def test_reports_word_counts(self):
        for chunk in chunk_markdown(MD_SAMPLE):
            self.assertEqual(chunk["words"], len(chunk["text"].split()))


if __name__ == "__main__":
    unittest.main()

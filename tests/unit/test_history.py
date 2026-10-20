"""Tests for conversation history: bounding, pinning, summaries, state."""

import unittest

from context_engineering.context import ComponentKind
from context_engineering.history import ConversationHistory


class TestBoundedHistory(unittest.TestCase):
    def test_window_bounded_and_archived(self):
        history = ConversationHistory(max_turns=3)
        for i in range(6):
            history.add("user", f"message number {i}")
        self.assertEqual(len(history.turns), 3)
        self.assertEqual(len(history.archived), 3)
        self.assertEqual(history.turns[-1].content, "message number 5")

    def test_recent_view(self):
        history = ConversationHistory(max_turns=5)
        for i in range(5):
            history.add("user", f"turn {i}")
        self.assertEqual(len(history.recent(2)), 2)

    def test_rejects_bad_window(self):
        with self.assertRaises(ValueError):
            ConversationHistory(max_turns=0)


class TestPinnedConstraints(unittest.TestCase):
    def test_pin_survives_window(self):
        history = ConversationHistory(max_turns=2)
        history.pin("Budget: answer in under 50 words.")
        for i in range(10):
            history.add("user", f"flood {i}")
        components = history.to_components()
        pinned = [c for c in components if c.id == "history-pinned"]
        self.assertEqual(len(pinned), 1)
        self.assertIn("Budget: answer", pinned[0].content)

    def test_no_duplicate_pins(self):
        history = ConversationHistory()
        history.pin("same note")
        history.pin("same note")
        self.assertEqual(len(history.pinned), 1)


class TestDroppedSummary(unittest.TestCase):
    def test_summary_only_when_turns_dropped(self):
        history = ConversationHistory(max_turns=3)
        self.assertIsNone(history.dropped_summary())
        for i in range(5):
            history.add("user", f"The user asked about topic {i} and we answered it.")
        summary = history.dropped_summary()
        self.assertIsNotNone(summary)
        self.assertIn("topic", summary)

    def test_summary_component_is_derived(self):
        history = ConversationHistory(max_turns=2)
        for i in range(4):
            history.add("user", f"question {i}")
        components = history.to_components()
        kinds = {c.id: c.kind for c in components}
        self.assertIn("history-summary", kinds)
        self.assertEqual(kinds["history-summary"], ComponentKind.DERIVED)
        self.assertEqual(kinds["history-recent"], ComponentKind.HISTORY)

    def test_empty_history_yields_no_components(self):
        self.assertEqual(ConversationHistory().to_components(), [])


class TestStateRoundTrip(unittest.TestCase):
    def test_state_round_trip_preserves_everything(self):
        history = ConversationHistory(max_turns=3)
        history.pin("Always cite sources.")
        for i in range(6):
            history.add("user", f"turn {i}")
        state = history.to_state()
        restored = ConversationHistory.from_state(state)
        self.assertEqual(restored.pinned, history.pinned)
        self.assertEqual(len(restored.turns), len(history.turns))
        self.assertEqual(len(restored.archived), len(history.archived))
        self.assertEqual(restored.turns[0].content, history.turns[0].content)


if __name__ == "__main__":
    unittest.main()

"""Tests for the observability trace: events, timings, redaction."""

import time
import unittest

from context_engineering.observability import ContextTrace, TraceEvent
from context_engineering.security import redact


class TestContextTrace(unittest.TestCase):
    def test_stage_records_event_with_duration(self):
        trace = ContextTrace()
        with trace.stage("retrieve", tokens_in=12) as event:
            event.notes["hits"] = 6
            _ = sum(range(1000))  # a tiny bit of work
        self.assertEqual(len(trace.events), 1)
        event = trace.events[0]
        self.assertEqual(event.stage, "retrieve")
        self.assertEqual(event.outcome, "ok")
        self.assertGreaterEqual(event.duration_ms, 0.0)
        self.assertEqual(event.tokens_in, 12)

    def test_failure_marks_event_failed(self):
        trace = ContextTrace()
        with self.assertRaises(RuntimeError):
            with trace.stage("fragile"):
                raise RuntimeError("boom")
        self.assertEqual(trace.events[0].outcome, "failed")
        self.assertEqual(trace.failures(), trace.events)

    def test_totals_aggregate(self):
        trace = ContextTrace()
        with trace.stage("a", tokens_in=10):
            pass
        with trace.stage("b", tokens_in=20, tokens_out=5):
            pass
        self.assertEqual(trace.total_tokens_in, 30)
        self.assertEqual(trace.total_tokens_out, 5)
        self.assertGreaterEqual(trace.total_duration_ms, 0.0)

    def test_dropped_ids_rendered_never_content(self):
        trace = ContextTrace()
        event = TraceEvent(stage="budget", outcome="ok", dropped=["ev-old-v1"])
        trace.add(event)
        rendered = trace.render()
        self.assertIn("ev-old-v1", rendered)
        self.assertNotIn("Employees may work", rendered)  # no payload text anywhere

    def test_render_redacts_sensitive_notes_by_default(self):
        trace = ContextTrace()
        with trace.stage("screen") as event:
            event.notes["excerpt"] = "user wrote to alice@nimbus-dynamics.example about PTO"
        rendered = trace.render()
        self.assertNotIn("alice@nimbus-dynamics.example", rendered)
        self.assertIn("[REDACTED:email]", rendered)

    def test_render_can_opt_out_of_redaction(self):
        trace = ContextTrace(redact_by_default=False)
        with trace.stage("s") as event:
            event.notes["key"] = "alice@nimbus-dynamics.example"
        self.assertIn("alice@", trace.render())

    def test_events_for_stage(self):
        trace = ContextTrace()
        with trace.stage("retrieve"):
            pass
        with trace.stage("assemble"):
            pass
        with trace.stage("retrieve"):
            pass
        self.assertEqual(len(trace.events_for("retrieve")), 2)


if __name__ == "__main__":
    unittest.main()

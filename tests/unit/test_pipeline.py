"""Tests for the Pipeline: stages, retries, fallbacks, degradation."""

import unittest

from context_engineering.pipeline import Pipeline, StageError


class TestPipeline(unittest.TestCase):
    def test_stages_merge_updates_in_order(self):
        pipeline = Pipeline("merge")
        pipeline.add_stage("a", lambda p, ctx: {"a": 1})
        pipeline.add_stage("b", lambda p, ctx: {"b": p["a"] + 1})
        result = pipeline.run({"start": 0})
        self.assertEqual(result, {"start": 0, "a": 1, "b": 2})

    def test_retry_then_success(self):
        calls = {"n": 0}

        def flaky(payload, ctx):
            calls["n"] += 1
            if calls["n"] < 3:
                raise RuntimeError("transient")
            return {"ok": True}

        pipeline = Pipeline("retry")
        pipeline.add_stage("flaky", flaky, retries=3)
        result = pipeline.run({})
        self.assertEqual(calls["n"], 3)
        self.assertTrue(result["ok"])

    def test_fallback_used_after_retries_exhausted(self):
        def always_fails(payload, ctx):
            raise RuntimeError("down")

        def fallback(payload, ctx):
            return {"degraded": True}

        pipeline = Pipeline("fallback")
        pipeline.add_stage("fragile", always_fails, retries=1, fallback=fallback)
        result = pipeline.run({})
        self.assertTrue(result.get("degraded"))

    def test_required_failure_raises_stage_error(self):
        def broken(payload, ctx):
            raise RuntimeError("boom")

        pipeline = Pipeline("required")
        pipeline.add_stage("critical", broken, retries=1)
        with self.assertRaises(StageError) as caught:
            pipeline.run({})
        self.assertEqual(caught.exception.stage_name, "critical")

    def test_optional_stage_skips_gracefully(self):
        def broken(payload, ctx):
            raise RuntimeError("nonessential down")

        pipeline = Pipeline("optional")
        pipeline.add_stage("nice_to_have", broken, required=False)
        pipeline.add_stage("essential", lambda p, ctx: {"done": True})
        result = pipeline.run({})
        self.assertTrue(result["done"])

    def test_trace_records_outcomes(self):
        trace = []
        pipeline = Pipeline("traced")
        pipeline.add_stage("ok", lambda p, ctx: {"a": 1})
        pipeline.add_stage("skipped", lambda p, ctx: (_ for _ in ()).throw(RuntimeError("x")), required=False)
        pipeline.add_stage(
            "recovered",
            lambda p, ctx: (_ for _ in ()).throw(RuntimeError("y")),
            fallback=lambda p, ctx: {"recovered": True},
        )
        pipeline.run({}, trace=trace)
        outcomes = {t["stage"]: t["outcome"] for t in trace}
        self.assertEqual(outcomes["ok"], "ok")
        self.assertEqual(outcomes["skipped"], "skipped")
        self.assertEqual(outcomes["recovered"], "fallback")

    def test_duplicate_stage_name_rejected(self):
        pipeline = Pipeline("dup")
        pipeline.add_stage("same", lambda p, ctx: {})
        with self.assertRaises(ValueError):
            pipeline.add_stage("same", lambda p, ctx: {})


if __name__ == "__main__":
    unittest.main()

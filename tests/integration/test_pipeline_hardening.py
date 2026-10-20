"""Integration tests: pipeline hardening patterns (Chapter 30).

The degradation ladder in practice — every stage fails somewhere on
purpose, and the pipeline either degrades gracefully (optional stage),
recovers (fallback), or fails loud with an explanation (required stage).
These tests are the executable version of Chapter 30's table.
"""

import unittest

from context_engineering.pipeline import Pipeline, StageError


def always_raises(payload, ctx):
    raise RuntimeError("downstream is down")


def make_request_pipeline(retrieval_broken=False, screening_broken=False, budget_broken=False):
    """The assistant request pipeline with controllable breakage."""
    pipeline = Pipeline("assistant-request")

    def retrieve(payload, ctx):
        if retrieval_broken:
            raise RuntimeError("index unavailable")
        return {"evidence_ids": ["a", "b"]}

    def empty_retrieval(payload, ctx):
        return {"evidence_ids": []}  # fallback: degrade to no evidence

    def screen(payload, ctx):
        if screening_broken:
            raise RuntimeError("screener timeout")
        return {"findings": 0}

    def budget(payload, ctx):
        if budget_broken:
            raise RuntimeError("estimator exploded")
        return {"allocated": 3}

    pipeline.add_stage("retrieve", retrieve, retries=1, fallback=empty_retrieval, required=True)
    pipeline.add_stage("screen", screen, required=False)  # degrade, don't die
    pipeline.add_stage("budget", budget, required=True)   # silent overflow is worse than failing
    return pipeline


class TestDegradationLadder(unittest.TestCase):
    def test_healthy_pipeline(self):
        result = make_request_pipeline().run({"question": "q"})
        self.assertEqual(result["evidence_ids"], ["a", "b"])
        self.assertEqual(result["allocated"], 3)

    def test_retrieval_falls_back_to_empty_evidence(self):
        result = make_request_pipeline(retrieval_broken=True).run({"question": "q"})
        self.assertEqual(result["evidence_ids"], [])       # degraded, not dead
        self.assertEqual(result.get("allocated"), 3)
        # Downstream still runs; the empty evidence drives refusal semantics,
        # not a crash (Chapters 10, 30).

    def test_screening_failure_degrades_gracefully(self):
        result = make_request_pipeline(screening_broken=True).run({"question": "q"})
        self.assertNotIn("findings", result)  # optional stage skipped
        self.assertEqual(result["allocated"], 3)

    def test_budget_failure_fails_loud(self):
        trace = []
        with self.assertRaises(StageError) as caught:
            make_request_pipeline(budget_broken=True).run({"question": "q"}, trace=trace)
        self.assertEqual(caught.exception.stage_name, "budget")
        outcomes = {t["stage"]: t["outcome"] for t in trace}
        self.assertEqual(outcomes["retrieve"], "ok")
        self.assertEqual(outcomes["screen"], "ok")

    def test_cascade_order_in_trace(self):
        trace = []
        make_request_pipeline(retrieval_broken=True).run({"question": "q"}, trace=trace)
        self.assertEqual([t["stage"] for t in trace], ["retrieve", "screen", "budget"])
        self.assertEqual(trace[0]["outcome"], "fallback")
        self.assertEqual(trace[0]["attempts"], 2)  # one retry, then fallback


class TestBoundedExecution(unittest.TestCase):
    def test_retries_are_bounded(self):
        calls = {"n": 0}

        def flaky(payload, ctx):
            calls["n"] += 1
            raise RuntimeError("always down")

        pipeline = Pipeline("bounded")
        pipeline.add_stage("x", flaky, retries=2, required=False)
        pipeline.run({})
        self.assertEqual(calls["n"], 3)  # initial + 2 retries, then give up — never a loop

    def test_required_failure_after_retries_raises(self):
        calls = {"n": 0}

        def flaky(payload, ctx):
            calls["n"] += 1
            raise RuntimeError("down")

        pipeline = Pipeline("bounded-required")
        pipeline.add_stage("y", flaky, retries=2, required=True)
        with self.assertRaises(StageError):
            pipeline.run({})
        self.assertEqual(calls["n"], 3)


if __name__ == "__main__":
    unittest.main()

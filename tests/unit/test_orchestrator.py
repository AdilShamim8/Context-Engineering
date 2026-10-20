"""Tests for the orchestrator: stages, checkpoints, resume."""

import unittest

from context_engineering.orchestrator import (
    Checkpoint,
    CheckpointStore,
    TaskState,
    Workflow,
)

calls: list = []


def stage_factory(name, update):
    def fn(state, ctx):
        calls.append(name)
        return update

    return fn


class TestWorkflow(unittest.TestCase):
    def setUp(self):
        calls.clear()
        self.workflow = Workflow("research")
        self.workflow.add_stage("plan", stage_factory("plan", {"plan": ["step-a", "step-b"]}))
        self.workflow.add_stage("retrieve", stage_factory("retrieve", {"chunks": 4}))
        self.workflow.add_stage("draft", stage_factory("draft", {"draft": "written"}))

    def test_stages_run_in_order(self):
        state = self.workflow.run(TaskState("t1"))
        self.assertEqual(calls, ["plan", "retrieve", "draft"])
        self.assertEqual(state.data["plan"], ["step-a", "step-b"])
        self.assertEqual(state.data["chunks"], 4)
        self.assertEqual(state.stage_history, ["plan", "retrieve", "draft"])

    def test_checkpoints_saved_after_each_stage(self):
        store = CheckpointStore()
        self.workflow.run(TaskState("t2"), checkpoint_store=store)
        checkpoint = store.load("t2")
        self.assertEqual(checkpoint.stages_done, ["plan", "retrieve", "draft"])
        self.assertEqual(checkpoint.remaining, [])
        self.assertEqual(checkpoint.outputs["draft"], "written")

    def test_resume_skips_completed_stages(self):
        # Run two stages, then "interrupt".
        store = CheckpointStore()
        workflow = Workflow("research")
        workflow.add_stage("plan", stage_factory("plan", {"plan": "done"}))
        workflow.add_stage("retrieve", stage_factory("retrieve", {"chunks": 4}))
        workflow.add_stage("draft", stage_factory("draft", {"draft": "written"}))

        state = TaskState("t3")
        workflow.run(state, checkpoint_store=store)  # runs all… pretend pause happened at stage 2 in real life
        # Simulate the real interruption: build a checkpoint with only the first two stages done.
        interrupted = Checkpoint(
            task_id="t3", stages_done=["plan", "retrieve"], outputs={"plan": "done", "chunks": 4}, remaining=["draft"]
        )
        calls.clear()
        resumed = workflow.resume(interrupted)
        self.assertEqual(calls, ["draft"])          # only the missing stage ran
        self.assertEqual(resumed.data["plan"], "done")  # state carried over
        self.assertEqual(resumed.data["draft"], "written")

    def test_trace_records_skips(self):
        trace = []
        interrupted = Checkpoint(
            task_id="t4", stages_done=["plan"], outputs={"plan": "done"}, remaining=["retrieve", "draft"]
        )
        self.workflow.resume(interrupted, trace=trace)
        outcomes = {t["stage"]: t["outcome"] for t in trace}
        self.assertEqual(outcomes["plan"], "skipped (already done)")
        self.assertEqual(outcomes["draft"], "ok")

    def test_duplicate_stage_rejected(self):
        with self.assertRaises(ValueError):
            self.workflow.add_stage("plan", lambda s, c: {})

    def test_checkpoint_round_trip(self):
        checkpoint = Checkpoint(
            task_id="t5", stages_done=["plan"], outputs={"a": 1}, remaining=["draft"], saved_at="2026-10-20T00:00:00+00:00"
        )
        restored = Checkpoint.from_dict(checkpoint.to_dict())
        self.assertEqual(restored.outputs, {"a": 1})
        state = TaskState.from_checkpoint(restored)
        self.assertEqual(state.task_id, "t5")
        self.assertEqual(state.stage_history, ["plan"])


if __name__ == "__main__":
    unittest.main()

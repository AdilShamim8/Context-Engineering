"""Multi-step workflows with per-stage context and checkpoints (Chapter 21).

An agent loop re-decides the context at every step. This module keeps
that honest by making the loop explicit:

- WorkflowStage: a named function (state, ctx) -> updates. Small stages,
  independently testable — the Pipeline's discipline (Chapter 10),
  specialized for task execution.
- TaskState: the working state: task id, data dict, and the stage
  history. This is Chapter 19's "state" artifact as code.
- Checkpoint / CheckpointStore: per-stage durability. After every stage,
  the workflow can checkpoint; ``resume`` re-enters the workflow with
  done-stages skipped and fresh context derived per remaining stage.

The teaching core (Chapter 19): checkpoints store DECISIONS AND OUTPUTS,
never derived context. Each stage rebuilds what it needs from state, so
corpus or policy changes between pause and resume are picked up
automatically — resume-rebuild beats replay.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class WorkflowStage:
    name: str
    fn: Callable  # (state: TaskState, ctx: dict) -> dict


class TaskState:
    """The working state of one task (Chapter 19's third artifact)."""

    def __init__(self, task_id: str, data: dict | None = None) -> None:
        self.task_id = task_id
        self.data: dict = dict(data or {})
        self.stage_history: list = []

    def checkpoint(self, remaining: list) -> "Checkpoint":
        return Checkpoint(
            task_id=self.task_id,
            stages_done=list(self.stage_history),
            outputs=dict(self.data),
            remaining=list(remaining),
            saved_at=_now_iso(),
        )

    @classmethod
    def from_checkpoint(cls, checkpoint: "Checkpoint") -> "TaskState":
        state = cls(task_id=checkpoint.task_id, data=dict(checkpoint.outputs))
        state.stage_history = list(checkpoint.stages_done)
        return state


@dataclass
class Checkpoint:
    task_id: str
    stages_done: list
    outputs: dict
    remaining: list
    saved_at: str = ""

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "stages_done": list(self.stages_done),
            "outputs": dict(self.outputs),
            "remaining": list(self.remaining),
            "saved_at": self.saved_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Checkpoint":
        return cls(
            task_id=data["task_id"],
            stages_done=list(data["stages_done"]),
            outputs=dict(data["outputs"]),
            remaining=list(data["remaining"]),
            saved_at=data.get("saved_at", ""),
        )


class CheckpointStore:
    """In-memory checkpoint store (swap in a real one in production)."""

    def __init__(self) -> None:
        self._checkpoints: dict = {}

    def save(self, checkpoint: Checkpoint) -> None:
        self._checkpoints[checkpoint.task_id] = checkpoint

    def load(self, task_id: str):
        return self._checkpoints.get(task_id)

    def task_ids(self) -> list:
        return sorted(self._checkpoints)


@dataclass
class Workflow:
    """An ordered multi-stage task executor with per-stage checkpointing."""

    name: str = "workflow"
    stages: list = field(default_factory=list)

    def add_stage(self, name: str, fn: Callable) -> "Workflow":
        if any(s.name == name for s in self.stages):
            raise ValueError(f"stage {name!r} already exists")
        self.stages.append(WorkflowStage(name=name, fn=fn))
        return self

    def run(
        self,
        state: TaskState,
        checkpoint_store: CheckpointStore | None = None,
        trace: list | None = None,
    ) -> TaskState:
        """Execute remaining stages, checkpointing after each one."""
        ctx = {"workflow": self, "trace": trace}
        for stage in self.stages:
            if stage.name in state.stage_history:
                if trace is not None:
                    trace.append({"stage": stage.name, "outcome": "skipped (already done)"})
                continue
            updates = stage.fn(state, ctx)
            if updates:
                state.data.update(updates)
            state.stage_history.append(stage.name)
            if trace is not None:
                trace.append({"stage": stage.name, "outcome": "ok"})
            if checkpoint_store is not None:
                remaining = [s.name for s in self.stages if s.name not in state.stage_history]
                checkpoint_store.save(state.checkpoint(remaining))
        return state

    def resume(
        self,
        checkpoint: Checkpoint,
        checkpoint_store: CheckpointStore | None = None,
        trace: list | None = None,
    ) -> TaskState:
        """Continue a checkpointed task, skipping completed stages."""
        state = TaskState.from_checkpoint(checkpoint)
        return self.run(state, checkpoint_store=checkpoint_store, trace=trace)

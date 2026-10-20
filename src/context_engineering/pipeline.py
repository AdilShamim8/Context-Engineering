"""Stage composition with retries, fallbacks, and graceful degradation
(Chapters 10, 30).

The Pipeline is the executable skeleton of the context engineering
lifecycle (Chapter 10): each stage is a named function that receives a
payload dict and returns updates to merge into it. Stages are small,
independently testable, and individually resilient:

- ``retries``: on failure, the stage re-runs (immediately — deterministic
  tests; production wrappers add backoff, Chapter 31).
- ``fallback``: a substitute function used when the stage keeps failing.
- ``required``: if a non-required stage fails, it is skipped and the
  payload flows on (graceful degradation); required stages raise
  StageError (fail loud where silence would corrupt the request).

A trace list, when provided, records every stage outcome — including
skips — so the observability layer (Chapter 29) can explain exactly what
the pipeline did. Stage functions must stay pure-ish: same payload in,
same updates out, no hidden globals.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional


class StageError(RuntimeError):
    """A required stage failed after retries and fallback."""

    def __init__(self, stage_name: str, cause: Exception):
        self.stage_name = stage_name
        self.cause = cause
        super().__init__(f"required stage {stage_name!r} failed: {cause!r}")


@dataclass
class PipelineStage:
    name: str
    fn: Callable
    retries: int = 0
    fallback: Optional[Callable] = None
    required: bool = True


@dataclass
class Pipeline:
    """An ordered composition of context-processing stages."""

    name: str = "pipeline"
    stages: list = field(default_factory=list)

    def add_stage(
        self,
        name: str,
        fn: Callable,
        retries: int = 0,
        fallback: Optional[Callable] = None,
        required: bool = True,
    ) -> "Pipeline":
        if any(s.name == name for s in self.stages):
            raise ValueError(f"stage {name!r} already exists in pipeline {self.name!r}")
        self.stages.append(
            PipelineStage(name=name, fn=fn, retries=retries, fallback=fallback, required=required)
        )
        return self

    def run(self, payload: dict, trace: list | None = None) -> dict:
        """Execute stages in order; merge each stage's updates into the payload.

        ``trace`` (optional list) receives dicts: stage, outcome, attempts,
        and notes. Never pass sensitive payloads through a trace you intend
        to store unredacted (Chapter 29).
        """
        payload = dict(payload)
        ctx = {"pipeline": self, "trace": trace}
        for stage in self.stages:
            attempts = 0
            outcome = None
            while True:
                attempts += 1
                try:
                    updates = stage.fn(payload, ctx)
                    if updates:
                        payload.update(updates)
                    outcome = "ok"
                    break
                except Exception as exc:  # noqa: BLE001 — stage isolation is the point
                    if attempts <= stage.retries:
                        continue
                    if stage.fallback is not None:
                        try:
                            updates = stage.fallback(payload, ctx)
                            if updates:
                                payload.update(updates)
                            outcome = "fallback"
                            break
                        except Exception as fallback_exc:  # noqa: BLE001
                            exc = fallback_exc
                    if stage.required:
                        raise StageError(stage.name, exc) from exc
                    outcome = "skipped"
                    break
            if trace is not None:
                trace.append(
                    {
                        "pipeline": self.name,
                        "stage": stage.name,
                        "outcome": outcome,
                        "attempts": attempts,
                    }
                )
        return payload

    def stage_names(self) -> list:
        return [s.name for s in self.stages]

"""Stage traces: timings, token counts, decisions — redacted by default (Chapter 29).

The trace contract this module enforces:

- Traces record STRUCTURE, not content: stage names, outcomes, durations,
  token counts, and small scalar/label notes. Payloads never enter a
  trace; the assembled request is the most sensitive artifact in the
  system (Ch. 25) and is never archived here.
- Redaction applies by default to any string note that slips in
  (credentials, emails) — defense in depth for the day someone forgets.
- Timings use time.monotonic (immune to wall-clock adjustments) and are
  recorded at stage granularity — the debugging unit of Chapter 4's
  diagnostic loop.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field

from .security import redact as _redact_text


@dataclass
class TraceEvent:
    stage: str
    outcome: str = "ok"          # ok | skipped | fallback | failed | custom
    duration_ms: float = 0.0
    tokens_in: int = 0
    tokens_out: int = 0
    dropped: list = field(default_factory=list)   # component/chunk ids — never text
    notes: dict = field(default_factory=dict)    # scalars and labels only


class ContextTrace:
    """A per-request trace of what the pipeline did."""

    def __init__(self, redact_by_default: bool = True) -> None:
        self.events: list = []
        self.redact_by_default = redact_by_default

    @contextmanager
    def stage(self, name: str, tokens_in: int = 0, tokens_out: int = 0, outcome: str = "ok"):
        """Record one stage: ``with trace.stage("retrieve") as ev: ...``."""
        event = TraceEvent(stage=name, tokens_in=tokens_in, tokens_out=tokens_out, outcome=outcome)
        start = time.monotonic()
        try:
            yield event
        except Exception:
            event.outcome = "failed"
            raise
        finally:
            event.duration_ms = round((time.monotonic() - start) * 1000.0, 3)
            self.events.append(event)

    def add(self, event: TraceEvent) -> None:
        self.events.append(event)

    # -- derived views ---------------------------------------------------

    def events_for(self, stage: str) -> list:
        return [e for e in self.events if e.stage == stage]

    @property
    def total_duration_ms(self) -> float:
        return round(sum(e.duration_ms for e in self.events), 3)

    @property
    def total_tokens_in(self) -> int:
        return sum(e.tokens_in for e in self.events)

    @property
    def total_tokens_out(self) -> int:
        return sum(e.tokens_out for e in self.events)

    def failures(self) -> list:
        return [e for e in self.events if e.outcome in ("failed", "fallback")]

    # -- rendering ---------------------------------------------------------

    def render(self, redact: bool | None = None) -> str:
        """Human-readable trace. Never includes payload content."""
        should_redact = self.redact_by_default if redact is None else redact
        lines = [f"{'STAGE':<18}{'OUTCOME':<10}{'MS':>10}{'TOK_IN':>8}  NOTES"]
        for event in self.events:
            notes = "; ".join(f"{k}={v}" for k, v in event.notes.items())
            if should_redact and notes:
                notes = _redact_text(notes)
            dropped = f" dropped={event.dropped}" if event.dropped else ""
            lines.append(
                f"{event.stage:<18}{event.outcome:<10}{event.duration_ms:>10.3f}"
                f"{event.tokens_in:>8}  {notes}{dropped}"
            )
        lines.append("-" * 60)
        lines.append(
            f"Total: {self.total_duration_ms:.3f} ms | "
            f"tokens in: {self.total_tokens_in} | "
            f"failed/fallback stages: {len(self.failures())}"
        )
        return "\n".join(lines)

"""Bounded conversation history with pinned constraints (Chapter 17).

Conversation history is the most commonly mis-budgeted component in
production (Chapter 12's worked example): appended without bound, it
silently consumes the window. This module implements the three mechanisms
that make history a managed component instead of an accident:

- ``max_turns``: the recent-turns window; older turns are *archived*
  (kept for summarization, not for the request).
- ``dropped_summary()``: a deterministic rolling summary of archived
  turns, built with compression.structured_notes — rung 5 of the
  compression ladder, not a model call.
- ``pinned`` constraints: facts/rules that must survive every turn
  (budget decisions, standing constraints), independent of the window.

State round-trip (to_state/from_state) supports Chapter 19's checkpoints.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

from .compression import structured_notes
from .context import ComponentKind, ContextComponent, TrustLevel


@dataclass
class Turn:
    role: str  # "user" | "assistant" (kept permissive for tool roles)
    content: str
    timestamp: str = ""
    meta: dict = field(default_factory=dict)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class ConversationHistory:
    """A bounded, inspectable conversation history."""

    def __init__(self, max_turns: int = 10) -> None:
        if max_turns < 1:
            raise ValueError("max_turns must be >= 1")
        self.max_turns = max_turns
        self.turns: list = []      # the live window
        self.archived: list = []   # turns that fell out of the window
        self.pinned: list = []     # constraints that must never fall out

    # -- mutation ---------------------------------------------------------

    def add(self, role: str, content: str) -> Turn:
        turn = Turn(role=role, content=content, timestamp=_now_iso())
        self.turns.append(turn)
        while len(self.turns) > self.max_turns:
            self.archived.append(self.turns.pop(0))
        return turn

    def pin(self, note: str) -> None:
        """Pin a constraint/fact so it survives the window and summaries."""
        if note not in self.pinned:
            self.pinned.append(note)

    # -- views ------------------------------------------------------------

    def recent(self, n: int | None = None) -> list:
        return list(self.turns[-n:]) if n else list(self.turns)

    def dropped_summary(self, max_tokens: int | None = 120) -> str | None:
        """Deterministic rolling summary of archived turns, or None."""
        if not self.archived:
            return None
        lines = [f"{t.role}: {t.content}" for t in self.archived]
        return structured_notes(lines, max_tokens=max_tokens)

    # -- context construction ----------------------------------------------

    def to_components(self, history_priority: int = 1) -> list:
        """Render history as budget-ready components.

        Pinned constraints come first (they outrank everything in history),
        then the rolling summary of dropped turns (DERIVED — the trace of
        compression must be visible in the request), then the live window.
        """
        components: list = []
        if self.pinned:
            components.append(
                ContextComponent(
                    id="history-pinned",
                    kind=ComponentKind.HISTORY,
                    content="Pinned constraints (apply at all turns):\n"
                    + "\n".join(f"- {note}" for note in self.pinned),
                    priority=history_priority,
                    trust=TrustLevel.NEUTRAL,
                )
            )
        summary = self.dropped_summary()
        if summary:
            components.append(
                ContextComponent(
                    id="history-summary",
                    kind=ComponentKind.DERIVED,
                    content=f"Summary of earlier turns (compressed):\n{summary}",
                    priority=history_priority,  # same tier: both survive or die together
                    trust=TrustLevel.NEUTRAL,
                    metadata={"compression": "structured_notes"},
                )
            )
        if self.turns:
            rendered = "\n".join(f"{t.role}: {t.content}" for t in self.turns)
            components.append(
                ContextComponent(
                    id="history-recent",
                    kind=ComponentKind.HISTORY,
                    content=rendered,
                    priority=history_priority,
                    trust=TrustLevel.NEUTRAL,
                )
            )
        return components

    # -- persistence (Chapter 19) -------------------------------------------

    def to_state(self) -> dict:
        return {
            "max_turns": self.max_turns,
            "turns": [asdict(t) for t in self.turns],
            "archived": [asdict(t) for t in self.archived],
            "pinned": list(self.pinned),
        }

    @classmethod
    def from_state(cls, state: dict) -> "ConversationHistory":
        history = cls(max_turns=state["max_turns"])
        history.turns = [Turn(**t) for t in state["turns"]]
        history.archived = [Turn(**t) for t in state["archived"]]
        history.pinned = list(state["pinned"])
        return history

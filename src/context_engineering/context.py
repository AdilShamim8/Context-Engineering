"""The component model: kinds, trust levels, and provenance (Chapter 3).

Every piece of information that can enter a model request is represented
as a ContextComponent with:

- a ``kind`` (the nine-way taxonomy from Chapter 3),
- a ``trust`` level (trusted instructions vs. untrusted retrieved data),
- an optional ``source`` (provenance: identity, version, dates, access),
- a ``priority`` (0 = most important, 9 = least) used by the allocator.

This small model is the backbone of the whole library: the budgeter
allocates components, the assembler orders and labels them, the security
module marks and wraps them, and the evaluator attributes outcomes to them.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Optional

from .tokens import heuristic_token_count


class TrustLevel(str, Enum):
    """Trust classification of context content (Chapter 3, 24)."""

    TRUSTED = "trusted"      # authored by the application: instructions, tool schemas, state
    UNTRUSTED = "untrusted"  # entered from outside: evidence, tool results
    NEUTRAL = "neutral"      # mixed/inherited: user input, history, memory


class ComponentKind(str, Enum):
    """The nine component kinds from Chapter 3."""

    INSTRUCTION = "instruction"
    USER_INPUT = "user_input"
    HISTORY = "history"
    EVIDENCE = "evidence"
    MEMORY = "memory"
    TOOL_DEFINITION = "tool_definition"
    TOOL_RESULT = "tool_result"
    STATE = "state"
    DERIVED = "derived"


@dataclass(frozen=True)
class SourceRef:
    """Provenance for a component: where its content came from.

    Carrying provenance is what makes citations, freshness checks, version
    selection, access filtering, and audit trails possible downstream.
    """

    source_id: str
    title: str = ""
    version: str = ""
    effective_date: str = ""  # ISO date, e.g. "2026-08-14"
    access: str = "public"    # authorization class, e.g. public/internal/restricted
    owner: str = ""
    retrieved_at: str = ""    # ISO datetime when the system fetched it

    def citation(self) -> str:
        """Human-readable citation label, e.g. 'hr-remote-work v2 (2026-08-14)'."""
        label = self.source_id
        if self.version:
            label += f" v{self.version}"
        if self.effective_date:
            label += f" ({self.effective_date})"
        return label


@dataclass
class ContextComponent:
    """One labeled piece of the model request (Chapter 3)."""

    id: str
    kind: ComponentKind
    content: str
    priority: int = 5  # 0 = most important; allocator sorts ascending
    trust: TrustLevel = TrustLevel.NEUTRAL
    source: Optional[SourceRef] = None
    label: str = ""
    metadata: dict = field(default_factory=dict)
    cached_tokens: Optional[int] = None

    def token_count(self, estimator=None) -> int:
        """Estimated token cost of this component (lazily computed)."""
        if self.cached_tokens is None:
            est = estimator or heuristic_token_count
            self.cached_tokens = max(0, int(est(self.content)))
        return self.cached_tokens

    def with_content(self, content: str) -> "ContextComponent":
        """Return a copy with different content (used by truncation)."""
        return replace(self, content=content, cached_tokens=None)

    @property
    def effective_label(self) -> str:
        return self.label or self.source.citation() if self.source else (self.label or self.kind.value)


class ContextBundle:
    """An ordered collection of components that will compete for a budget."""

    def __init__(self) -> None:
        self.components: list[ContextComponent] = []

    def add(self, component: ContextComponent) -> "ContextBundle":
        self.components.append(component)
        return self

    def total_tokens(self) -> int:
        return sum(c.token_count() for c in self.components)

    def by_kind(self) -> dict[ComponentKind, list[ContextComponent]]:
        grouped: dict[ComponentKind, list[ContextComponent]] = {}
        for comp in self.components:
            grouped.setdefault(comp.kind, []).append(comp)
        return grouped

    def find(self, component_id: str) -> Optional[ContextComponent]:
        for comp in self.components:
            if comp.id == component_id:
                return comp
        return None

    def __iter__(self):
        return iter(self.components)

    def __len__(self) -> int:
        return len(self.components)

    def __getitem__(self, index: int) -> ContextComponent:
        return self.components[index]

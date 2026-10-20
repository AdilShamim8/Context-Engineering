"""Ordering and labeled rendering of selected components (Chapters 13, 24).

Ordering is an engineering decision, not cosmetic: long-context research
(Liu et al., 2023) shows position can matter, so the library treats
strategy as explicit and testable rather than incidental string order.

Labeling is a *security* decision: untrusted components are wrapped in
unambiguous delimiters so that downstream processors (and eventually a
model) can never confuse retrieved data with application instructions.
The delimiters are a containment aid, not a security boundary on their
own — see Chapter 24 for the full layered-defense picture.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .context import ComponentKind, ContextComponent, TrustLevel
from .tokens import heuristic_token_count


class OrderingStrategy(str, Enum):
    STABLE = "stable"              # as given
    PRIORITY_ORDER = "priority"    # most important first (Chapter 12 alignment)
    PRIORITY_REVERSED = "priority_reversed"  # most important last (long-context heuristic)
    KIND_GROUPED = "kind_grouped"  # grouped by kind, instructions first


#: Canonical kind order for KIND_GROUPED: trusted framing first, evidence after.
KIND_ORDER = (
    ComponentKind.INSTRUCTION,
    ComponentKind.STATE,
    ComponentKind.TOOL_DEFINITION,
    ComponentKind.USER_INPUT,
    ComponentKind.HISTORY,
    ComponentKind.MEMORY,
    ComponentKind.EVIDENCE,
    ComponentKind.TOOL_RESULT,
    ComponentKind.DERIVED,
)


def order_components(
    components,
    strategy: OrderingStrategy = OrderingStrategy.KIND_GROUPED,
) -> list[ContextComponent]:
    """Return ``components`` reordered according to ``strategy`` (stable)."""
    items = list(components)
    if strategy is OrderingStrategy.STABLE:
        return items
    if strategy is OrderingStrategy.PRIORITY_ORDER:
        return sorted(items, key=lambda c: c.priority)
    if strategy is OrderingStrategy.PRIORITY_REVERSED:
        return sorted(items, key=lambda c: c.priority, reverse=True)
    # KIND_GROUPED
    return sorted(
        items,
        key=lambda c: (KIND_ORDER.index(c.kind), c.priority),
    )


def render_component(component: ContextComponent) -> str:
    """Render one component with a labeled header.

    Trusted components render as ``## [kind | trust]\\ncontent``.
    Untrusted components are additionally wrapped in explicit delimiters:

        ## [evidence | untrusted] hr-remote-work v2 (2026-08-14)
        <<<UNTRUSTED
        ...content...
        >>>

    The delimiters make the trust boundary visible in the assembled text
    itself: anything between <<<UNTRUSTED and >>> is data, never instructions.
    """
    header = f"## [{component.kind.value} | {component.trust.value}]"
    if component.source is not None:
        header += f" {component.source.citation()}"
    if component.trust is TrustLevel.UNTRUSTED:
        return f"{header}\n<<<UNTRUSTED\n{component.content}\n>>>"
    return f"{header}\n{component.content}"


@dataclass
class AssembledContext:
    """The final request text plus a map back to its components."""

    text: str
    spans: dict = field(default_factory=dict)  # component id -> (start, end)
    tokens: int = 0
    components: list = field(default_factory=list)  # ordered components

    def component_text(self, component_id: str) -> str:
        """Return the rendered text of one component by id (raises KeyError)."""
        start, end = self.spans[component_id]
        return self.text[start:end]

    def contains(self, snippet: str) -> bool:
        return snippet in self.text


def assemble(
    components,
    strategy: OrderingStrategy = OrderingStrategy.KIND_GROUPED,
    header: str = None,
) -> AssembledContext:
    """Order, label, and serialize components into the request text."""
    ordered = order_components(components, strategy)
    parts: list[str] = []
    spans: dict = {}
    offset = 0

    if header:
        parts.append(header)
        offset = len(header) + 2  # account for the "\n\n" joiner

    for comp in ordered:
        rendered = render_component(comp)
        spans[comp.id] = (offset, offset + len(rendered))
        parts.append(rendered)
        offset += len(rendered) + 2

    text = "\n\n".join(parts)
    return AssembledContext(
        text=text, spans=spans, tokens=heuristic_token_count(text), components=ordered
    )

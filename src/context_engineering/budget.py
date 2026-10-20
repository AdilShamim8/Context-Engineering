"""Priority-based context budgeting and allocation (Chapter 12).

The allocator answers one question: given more candidates than fit, what
gets in, what gets cut, and what gets dropped — and can it explain itself?

Policy, in order:

1. INSTRUCTION components are allocated first and must fit. Instructions
   that alone exceed the available budget raise BudgetError: a request whose
   instructions do not fit is not a graceful-degradation situation.
2. Remaining components are considered by ascending ``priority``
   (0 = most important), stable within equal priorities.
3. A component that fits entirely is included.
4. A component of a truncatable kind (evidence, memory, history, tool
   results, derived) that does not fit is head-truncated to the remaining
   space with a visible marker — provided the remaining space is at least
   ``MIN_TRUNCATED_TOKENS``; otherwise it is dropped.
5. Everything else is dropped with a recorded reason.

The result is a full audit trail: every candidate appears exactly once in
``records`` with its action and reason. Allocation reports are the primary
debugging artifact for Chapter 4's "excessive length" and "lossy
transformation" failures.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .context import ComponentKind, ContextComponent
from .tokens import heuristic_token_count

#: Kinds eligible for head-truncation instead of dropping.
TRUNCATABLE_KINDS = (
    ComponentKind.EVIDENCE,
    ComponentKind.MEMORY,
    ComponentKind.HISTORY,
    ComponentKind.TOOL_RESULT,
    ComponentKind.DERIVED,
)

#: Below this remaining space, truncation is pointless — drop instead.
MIN_TRUNCATED_TOKENS = 32

TRUNCATION_MARKER = " …[truncated to fit context budget]"


class BudgetError(ValueError):
    """Raised when instructions alone cannot fit the available budget."""


@dataclass
class ContextBudget:
    """The token capacity for one request (Chapter 2's three budgets)."""

    total_tokens: int = 8192
    reserved_output_tokens: int = 1024
    safety_margin_tokens: int = 128

    @property
    def available_for_context(self) -> int:
        return max(
            0,
            self.total_tokens
            - self.reserved_output_tokens
            - self.safety_margin_tokens,
        )


@dataclass
class AllocationRecord:
    """What happened to one candidate component during allocation."""

    component_id: str
    kind: str
    priority: int
    action: str  # "included" | "truncated" | "dropped"
    tokens_original: int
    tokens_included: int
    reason: str = ""


@dataclass
class AllocationResult:
    budget: ContextBudget
    records: list[AllocationRecord] = field(default_factory=list)
    selected: list[ContextComponent] = field(default_factory=list)

    @property
    def total_allocated(self) -> int:
        return sum(rec.tokens_included for rec in self.records if rec.action != "dropped")

    @property
    def dropped_ids(self) -> list[str]:
        return [rec.component_id for rec in self.records if rec.action == "dropped"]

    def report(self) -> str:
        """Render a compact, human-readable allocation report."""
        lines = [
            f"Budget: {self.budget.total_tokens} total, "
            f"{self.budget.reserved_output_tokens} reserved output, "
            f"{self.budget.safety_margin_tokens} margin → "
            f"{self.budget.available_for_context} available",
            f"Allocated: {self.total_allocated} tokens across {len(self.selected)} components",
            f"{'ID':<24}{'KIND':<16}{'PRI':<4}{'ACTION':<10}{'TOKENS':<13}REASON",
        ]
        for rec in self.records:
            tokens = f"{rec.tokens_included}/{rec.tokens_original}"
            lines.append(
                f"{rec.component_id:<24}{rec.kind:<16}{rec.priority:<4}"
                f"{rec.action:<10}{tokens:<13}{rec.reason}"
            )
        return "\n".join(lines)


def _truncate_to_fit(content: str, token_limit: int, marker: str = TRUNCATION_MARKER) -> str:
    """Head-truncate ``content`` (word-aligned) until it fits ``token_limit``."""
    words = content.split()
    if not words:
        return content
    candidate = " ".join(words)
    while heuristic_token_count(candidate + marker) > token_limit and len(words) > 1:
        words = words[: max(1, int(len(words) * 0.9))]
        candidate = " ".join(words)
    return candidate + marker


def allocate(
    components,
    budget: ContextBudget,
    truncatable_kinds=TRUNCATABLE_KINDS,
    marker: str = TRUNCATION_MARKER,
) -> AllocationResult:
    """Allocate ``components`` (a bundle or list) under ``budget``.

    See the module docstring for the policy. Returns an AllocationResult
    whose ``selected`` components are safe to assemble: their combined
    cost never exceeds ``budget.available_for_context``.
    """
    if hasattr(components, "components"):  # accept a ContextBundle
        components = list(components.components)
    else:
        components = list(components)

    result = AllocationResult(budget=budget)
    remaining = budget.available_for_context

    instructions = [c for c in components if c.kind is ComponentKind.INSTRUCTION]
    others = [c for c in components if c.kind is not ComponentKind.INSTRUCTION]

    # Policy 1: instructions must fit — full stop.
    instruction_tokens = sum(c.token_count() for c in instructions)
    if instruction_tokens > budget.available_for_context:
        raise BudgetError(
            f"instructions alone need {instruction_tokens} tokens but only "
            f"{budget.available_for_context} are available; shorten the instructions "
            f"or raise the budget"
        )

    # Policy 2: others by priority (stable within a priority).
    others.sort(key=lambda c: c.priority)

    for comp in instructions + others:
        cost = comp.token_count()
        if cost <= remaining:
            result.selected.append(comp)
            remaining -= cost
            action, tokens_in, reason = "included", cost, ""
        elif (
            comp.kind in truncatable_kinds
            and remaining >= MIN_TRUNCATED_TOKENS
        ):
            truncated = comp.with_content(_truncate_to_fit(comp.content, remaining, marker))
            kept = truncated.token_count()
            result.selected.append(truncated)
            remaining -= kept
            action, tokens_in = "truncated", kept
            reason = f"truncated from {cost} tokens to fit remaining space"
        else:
            action, tokens_in = "dropped", 0
            reason = (
                f"insufficient budget: needed {cost}, {max(remaining, 0)} left "
                f"(priority {comp.priority})"
            )
        result.records.append(
            AllocationRecord(
                component_id=comp.id,
                kind=comp.kind.value,
                priority=comp.priority,
                action=action,
                tokens_original=cost,
                tokens_included=tokens_in,
                reason=reason,
            )
        )

    return result

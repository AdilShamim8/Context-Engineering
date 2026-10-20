# Lab 13 — Ordering and Compression Under Budget

> Time: ~50 minutes · Deterministic · Chapter tie-ins: 13, 14
> Success criterion: you demonstrate mechanical position loss and beat it with compression — on the same budget

## Objective

Two experiments that together kill the "context is a string" mental model: (1) the same components, differently ordered, lose different content under one budget; (2) deliberate compression rescues content that truncation would have destroyed.

## Setup

```python
from context_engineering.assembly import OrderingStrategy, assemble
from context_engineering.budget import ContextBudget, allocate
from context_engineering.compression import extractive_compress
from context_engineering.context import ComponentKind, ContextComponent, SourceRef, TrustLevel
```

Build a bundle: instructions (trusted, priority 0), one 600-token policy component (evidence, priority 1, containing a rule with a number and a date), three filler evidence components (priorities 3–5, chatty), one tool result (priority 2, 400 tokens, the meeting time buried mid-payload).

## Experiment 1 — order decides who gets cut

1. Set the budget so that instructions + policy + tool result fit, but not all fillers (compute from your ledger, Chapter 12 style).
2. Assemble under all four `OrderingStrategy` values and record, for each: the allocation report, and where the policy component landed (`AssembledContext.spans`).
3. Predict first: which ordering cuts a filler's *head*, which cuts its tail? Verify against reports.

## Experiment 2 — compression beats truncation

1. Shrink the budget by 30%. Now the policy component itself gets truncated under allocation.
2. Before allocation, run `extractive_compress(policy_text, max_tokens=...)` sized to fit. Assemble.
3. Diff the two assembled contexts: what did truncation keep vs. what did compression keep? Confirm your task's loss budget (the number and the date) survived in both. If it survived in one and not the other, write down which rungs of Chapter 14's ladder each path corresponds to.

## Deliverables

A two-table report: (A) strategy → what got cut (with span evidence); (B) truncation vs. compression → content survived/lost. Plus one paragraph: your recommendation for this corpus's ordering default, and the evidence behind it.

## Definition of success

You can state, with span and report citations from your own run: "under budget B, ordering X loses content class Y, and compression rung R preserves content class Z" — and your paragraph's recommendation names its evidence. If your prediction was wrong somewhere, include it; miscalibration is the lab's best output.

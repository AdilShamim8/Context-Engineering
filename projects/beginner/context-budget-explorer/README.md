# Project — Context Budget Explorer (Beginner)

> Tier: Beginner · Prerequisites: Parts I–III (Chapters 2, 12)
> Implementation: `src/context_engineering/{budget,tokens}.py` + CLI `budget` · Tests: `tests/unit/test_budget.py`, `test_cli.py`

## Objective

Build the tool you will use for the rest of your career every time someone says "we're running out of context": a budget explorer that takes a component bundle, allocates it under a chosen window, and shows — per component — what survived, what got truncated, and what got dropped, with reasons.

## The tool, as shipped

```bash
# default: deliberately tight budget (2000 tokens) over the 10-component demo bundle
PYTHONPATH=src python -m context_engineering.cli budget

# your own window and output reservation
PYTHONPATH=src python -m context_engineering.cli budget --total 4096 --reserved-output 1024
```

The demo bundle (`datasets/synthetic/demo_bundle.json`) is a realistic assistant request — instructions, state, two history turns, a memory note, a tool definition, three evidence items (including a stale v1 policy), and a big chatty tool result — sized so pressure produces interesting decisions rather than everything-fits tedium.

## Your work on this project

1. **Run the report at three budgets** (generous / tight / impossible) and annotate each with one sentence per interesting row: *why* that row got that fate.
2. **Find the cliff.** Binary-search the `--total` value at which (a) the stale evidence first drops, (b) the tool result first truncates, (c) the instructions fail. Report the three thresholds and what changes between them.
3. **Break the priority system** (deliberately): edit the bundle so every evidence item has priority 0. Re-run. Read the report and explain in one paragraph what the allocator degenerated into and what upstream lesson that encodes.
4. **Extend the explorer** (stretch): add `--strategy` to compare allocations under two orderings, printing both reports side by side.

## Deliverables

- Three annotated reports (from step 2) with the cliff thresholds.
- The priority-theater paragraph (step 3).
- (Stretch) your side-by-side output.

## Evaluation criteria

| Criterion | Pass standard |
|---|---|
| Report literacy | Each annotation names the policy line responsible (not "it didn't fit") |
| Cliff finding | Thresholds are exact and reproducible from your commands |
| Diagnosis | The priority-theater explanation identifies insertion-order degradation |

## Definition of success

Given any allocation report, you can reconstruct the request's fate without re-running — and you have caught yourself thinking "the budget decided that," which is the point.

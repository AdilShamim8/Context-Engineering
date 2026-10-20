# Project — Multi-Step Context Orchestrator (Advanced)

> Tier: Advanced · Prerequisites: Part V (Chapters 20–22)
> Implementation: `src/context_engineering/{orchestrator,tools,selection,budget,assembly}.py` · Tests: `tests/unit/test_orchestrator.py`, `test_tools.py`

## Objective

Build the research workflow from Chapter 21 end-to-end and then attack it: interrupt it, drift its corpus under it, deny one of its tools mid-run, and make two of its stages disagree — proving from traces and checkpoints that the architecture holds.

## Requirements

1. **Four stages minimum**: `plan` (decompose question into sub-queries), `retrieve` (per sub-query, access-filtered, version-aware), `select` (composite selection), `draft` (assemble + answer with citations + resumption brief).
2. **Per-stage context visibility**: each stage's assembled request is dumpable (`--show-stage-context stage_name`), and no stage's context contains another stage's raw transcript.
3. **Durability**: checkpoint after every stage; `resume` must work from any checkpoint with the corpus re-derived (no stale chunk contents in state — ids and scores only).
4. **A verify stage** (bonus, but expected at this tier): citation check of the draft against state's selected ids.

## The attack drills (the real deliverable)

1. **Interrupt & drift**: pause after `retrieve`; bump `hr-vacation` to v4 in the manifest (edit the corpus file; add a manifest entry); resume. Prove from the resumed `select`/`draft` outputs that v4 content was used.
2. **Mid-run tool denial**: change the caller's access set between stages so `retrieve`'s tool is denied on resume. The workflow must degrade per your Chapter 10 ladder (refuse with a reason, or re-plan without that source) — never crash, never hallucinate the missing data.
3. **Conflicting sub-answers**: engineer a question whose two sub-queries retrieve contradictory chunks (the corpus's v1/v2 conflict is available). The merge/draft stage must flag, then re-derive from cited ids — the test must fail if you implement coin-flipping.
4. **Token ledger**: report total tokens across all stages for 3 questions, before and after observation extraction (Chapter 21's rungs). The savings number is part of the deliverable.

## Deliverables

- The workflow + CLI entry to run, dump stage contexts, checkpoint, and resume.
- Four drill reports, each with the trace excerpt proving the behavior.
- The extraction savings table.

## Evaluation criteria

| Criterion | Pass standard |
|---|---|
| Isolation | Stage-context dumps show zero transcript carryover |
| Durability | All three resume paths work: clean, drift, denial |
| Honesty | Conflict drill demonstrably refuses to coin-flip |
| Economy | Ledger numbers reproducible from your commands |

## Definition of success

You can hand a teammate a checkpoint file and the manifest v4, they can resume on their machine, and the transcript shows the workflow absorbing both the interruption and the drift without you in the room.

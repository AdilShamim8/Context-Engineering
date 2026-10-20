# Project — Evidence and Source Manager (Advanced)

> Tier: Advanced · Prerequisites: Part II (Chapters 5, 9) + Part IV (Chapter 18)
> Implementation: `src/context_engineering/provenance.py` + `memory.py` patterns

## Objective

Build the source-lifecycle system Chapter 9 and Chapter 26 describe: the component that answers "which version is current, how fresh is it, who may read it, and what happens when sources disagree" — with every decision recorded and every behavior tested.

## Requirements

1. **Source registry** around the corpus manifest: current/superseded states, supersession chains (v1 ← v2 ← v3), owner per source, access classes.
2. **The four policies, executable**: version selection (newest-wins + keep-and-label mode), freshness (exclude/label/allow with verdicts that explain themselves), access (fail-closed), and conflict flagging (numeric + overlap detection).
3. **The lifecycle API**: `ingest`, `supersede(old, new, reason)`, `expire_source`, `restore` (rollback support — the tuple rewind of Ch. 32 at source granularity), with an audit event per operation (the memory store's audit pattern, transposed).
4. **The conflict theater**: a scripted v2/v3 disagreement arriving mid-week — show flag → decision (your policy, written down) → audit trail → downstream golden cases updated in the same change set.

## Deliverables

- The registry + policies (extension, tested).
- The scripted lifecycle run with audit annotations.
- The one-page policy document: your choices for each of the four policies and their failure-story justifications.

## Evaluation criteria

| Criterion | Pass standard |
|---|---|
| Completeness | All four policies executable with verdicts/reasons |
| Auditability | Every mutation leaves a reason-bearing event |
| Rollback | Supersede + restore round-trips; cases revert coherently |
| Honesty | Keep-and-label mode exists with its trade-off documented |

## Definition of success

A teammate can ask "why did the assistant say that in March?" about *your* registry and get the answer from the audit chain in under a minute — the Chapter 26 reconstruction, working.

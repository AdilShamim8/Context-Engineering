# Project — Conversation and Memory Manager (Intermediate)

> Tier: Intermediate · Prerequisites: Part IV (Chapters 17–19)
> Implementation: `src/context_engineering/{history,memory}.py` · Tests: `tests/unit/test_{history,memory}.py`

## Objective

Build a session manager that survives its own sessions: bounded history with pinned constraints and rolling summaries, an audited memory store with conflict handling and expiry, and resumable task state — then drive all three through a scripted multi-session scenario and show the system behaving deliberately at every step.

## Requirements

1. **Session lifecycle.** Start a session, run scripted turns, end it; start a *second* session the next "day" and prove the manager reconstructs a useful request (history window + summary + pinned + relevant memories).
2. **Conflict theater.** Script a user correcting a fact between sessions. Show: the conflict flagged on upsert, your chosen policy applied (supersede), the audit trail annotated, and the second session answering with the corrected value.
3. **Stale memory drill.** Store a TTL'd episodic memory, advance the clock (inject `today`), and show: expired memories invisible at retrieval, purge recorded with reasons.
4. **Deletion drill.** "Forget the performance note." Delete it, show the audit entry, and run the copy-hunt across history archive and rolling summary (the honest place this project finds leftovers).

## Deliverables

- The manager (composing `history.py` + `memory.py`; extension, not fork).
- A scenario script (`script.py`) executing all four drills with printed, annotated evidence.
- Test modules covering the four requirements (extend, don't duplicate, the existing unit tests).
- The written deletion checklist from the copy-hunt, with one paragraph on the boundary design.

## Evaluation criteria

| Criterion | Pass standard |
|---|---|
| Deliberateness | Every scripted step's outcome is a *policy result*, visible in audit/components |
| Conflict honesty | Flag → policy decision → audit, in that order, machine-readable |
| Deletion honesty | Copy-hunt documents any leftover found (or proves none) |
| Resume | Second session works with first session's window aged out (summary carrying commitments) |

## Definition of success

Your scenario transcript reads like a system with policies instead of a log with hopes: every "it remembered / it forgot / it corrected" line traces to a named mechanism.

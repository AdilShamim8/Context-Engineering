# Chapter 36 — Memory-Enabled Stateful Assistant

> Part IX · Integration and Capstone
> Prerequisites: Chapter 35, Part IV · Status: complete
> Time: ~75 minutes

## Overview

The knowledge assistant answers; the memory-enabled assistant *knows who it's talking to and where it left off*. This chapter is the integration of Part IV into the capstone: bounded conversation history with pinned constraints, an audited memory store feeding the request, and resumable sessions built on checkpoints. The design question throughout: **which of the three persistence layers (Ch. 19) does each new capability live in** — and what does it cost in budget, privacy surface, and blast radius?

## The session object: composition, not invention

Nothing new is built; two existing modules compose around the assistant:

```python
@dataclass
class Session:
    user_id: str
    access_levels: tuple
    history: ConversationHistory     # Ch. 17: bounded window + pinned + rolling summary
    memory: MemoryStore              # Ch. 18: audited, access-filtered, expirable
    checkpoint: Checkpoint | None    # Ch. 19: task state, if a task is open
```

The request path gains one stage between selection and budget: **memory retrieval** — `store.retrieve(question, k=4, access_policy=...)` whose hits become MEMORY components (semi-trusted, provenance `memory-store`, priority 2) — and the budget gains their cost. That is the whole integration, and its smallness is the point: the component model (Ch. 3) made the capstone *ready* for memory without modification. When a module needs no changes to gain a capability, the earlier architecture was right.

## What memory changes, by request stage

- **Selection**: memory components compete with evidence for budget (Ch. 12's ledger grows a line); pin the user's standing constraints (plan tier, communication preferences) at priority 2 and let task memories earn priority 3–4.
- **Assembly**: MEMORY renders between state and evidence (KIND_GROUPED's order — instructions/state first, the *person* next, documents last) — an ordering that is also semantically right: the model meets the task, then the user, then the material.
- **Response**: answers may now cite memory provenance ("user-stated, 2026-09-30") — and *must*, because an answer grounded in memory without provenance is unauditable (Ch. 26) and a memory conflict waiting to happen (Ch. 18).

## Session lifecycle: resume with the acid test applied

The session's `to_state()` bundles history state + memory state + checkpoint. Resume runs Chapter 19's acid test literally: rebuild from the bundle with *nothing else in memory* — history reconstructs its window and rolling summary from `archived`, memory re-injects its records, and any open task re-enters the orchestrator at its first missing stage. The session brief (a DERIVED component, ≤60 tokens: "Resuming: employee policy Q&A; last topic: relocation notices; open question: none.") orients the model — the piece most "stateful assistants" forget, producing the classic "resumed amnesia" users describe as "it doesn't remember anything."

The privacy note, once, because Part IV demanded it: a persistent session bundle is exactly the artifact Chapter 25's deletion design must cover. The copy-hunt drill from the conversation-memory project becomes a session-scoped audit: delete a memory → re-run the session → confirm the rolling summary, the checkpointed state, and the next request's assembled context all omit it. The deletion that survives its own copy-hunt is the one that exists.

## Memory extraction: the discipline gate

The upgrade's riskiest new surface is *what the system chooses to remember*. Run Chapter 18's minimization checklist as an explicit gate: propose candidates (user-stated corrections, preferences, commitments) → filter (transient? sensitive? inferable?) → store the survivors with source/confidence → audit. The failure mode to design against is the helpful-memory trap: an assistant that remembers everything ("you mentioned feeling tired Thursday") is not more helpful; it is a subpoena waiting to happen. The default posture of this curriculum — remember less, provenance-carry what you keep — is not caution for its own sake; it is what makes the memory system defensible.

## Exercises

1. **Beginner** — Build `Session` and run a 3-turn scripted conversation where turn 2 pins a constraint ("answers in under 20 words") and turn 4 tests that it held. Show the pinned component in the assembled context.
2. **Intermediate** — Script the conflict arc across sessions: state the stipend wrong, correct it, ask a day later. Show the flagged `numeric_mismatch`, your supersession policy's application, the audit trail, and the final answer citing the corrected record.
3. **Advanced** — The full stateful capstone run: interrupted multi-question task (checkpointed), a corpus version bump mid-pause, resume absorbing the drift, then the deletion drill on one memory with the copy-hunt. Deliverable: the evidence pack — traces, audit, and the before/after assembled contexts for the deletion.

## Mastery checklist

- [ ] I can add memory to the request path with zero changes to upstream stages — and explain why that was possible.
- [ ] I can run a session that survives the empty-everything resume test, with a session brief.
- [ ] I can pass the memory deletion copy-hunt on my own session bundle.

## Next

Chapter 37: a different domain — the same machinery for a repository-aware coding assistant.

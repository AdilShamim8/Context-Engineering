# Chapter 21 — Context Across Multi-Step Agent Workflows

> Part V · Tools, Agents, and Multimodal Context
> Prerequisites: Chapters 19, 20 · Status: complete
> Time: ~60 minutes

## Overview

An agent is a loop: decide → act → observe → re-decide. Each turn of that loop re-answers the entire Part III question set — *what does the model need to see **this** step?* — and the accumulated history of its own actions becomes the biggest context-management problem in the field. This chapter covers per-stage context, handoffs, intermediate artifacts, and the compaction that keeps long tasks viable. `orchestrator.py` is the executable core: named stages, per-stage checkpoints, and resume that re-derives rather than replays.

## The accumulating-context problem

A 15-step workflow with naive context management re-sends everything each turn: instructions (~300), tool definitions (~200), and — the killer — every observation so far (~150–400 each). By step 10 the request is mostly *history of its own actions*, and Chapter 2's three-way squeeze is fully in force: the current step's evidence competes with the residue of solved steps. Production agent stacks converge on the same fixes (Anthropic's agent guidance names compaction and structured note-taking as core operations; reviewed 2026-10-20), and this chapter builds them:

- **Per-stage context**: each stage's function receives what *it* needs, not the whole backlog — the orchestrator's `WorkflowStage` signature `(state, ctx)` forces that boundary at the type level.
- **Task state over conversational residue**: intermediate results live in `TaskState.data` (Chapter 19's state artifact), not in an ever-growing transcript. The transcript is what happened; state is what's true.
- **Derived artifacts, labeled**: when a stage's output must persist into later contexts, it enters as a DERIVED component with its provenance chain — never as anonymous text.

## Stages, handoffs, and the "context handoff" pattern

Between stages, the orchestrator hands off *state*, and each stage rebuilds context from it. Read the difference carefully — it is Chapter 19's whole argument in miniature:

> **Transcript handoff** (anti-pattern): each stage receives the previous stage's full assembled context plus its own additions. Cheap to write; accumulates; goes stale after any pause.
>
> **State handoff** (pattern): each stage receives structured state; it derives its own context (re-retrieving under current policies, re-filtering access, re-checking versions). Costs a little per stage; never accumulates; drift-correct after any pause.

The orchestrator's `resume` makes the payoff testable: interrupt after stage 2, change the corpus, resume — the third stage re-derives against the *new* corpus because only its inputs, not its inputs' contexts, were checkpointed. The test suite proves it with a calls-counter: resumed workflows execute exactly the missing stages.

## Checkpoints per stage

`CheckpointStore.save` fires after *every* stage — not because every workflow is long, but because the cost is one dict write and the benefit is crash-resume at stage granularity. The checkpoint contains `stages_done`, `outputs`, and `remaining` — decisions and pointers, per Chapter 19. Two design notes worth keeping: checkpoints are a **privacy surface** (they persist task outputs; Chapter 25's retention rules apply to them like anything else), and they are **not an audit trail** — the trace is for explaining, the checkpoint is for resuming; conflating them produces both done badly.

## The observe-decide boundary: trimming tool results before they accumulate

Chapter 20 bounded individual tool results; the workflow-level question is *whether an observation needs to persist at all*. The durable pattern (three rungs of Chapter 14's ladder applied to observations):

1. **Extract at observation time**: when a tool result arrives, immediately derive what the task needs (numbers, ids, statuses) into state; the raw result is then droppable.
2. **Summarize solved steps**: once stage N's decision is made from an observation, later stages need the *decision*, not the observation — replace with a structured note ("deploy verified: flag at 100%, error budget clean").
3. **Never let raw payloads cross stage boundaries twice.** If stage 5 needs stage 3's raw output again, that is a re-fetch (Chapter 15's on-demand retrieval), not a carry-along.

Anthropic's framing of agent-context operations (compaction, note-taking) is exactly this discipline observed in production; our version is deterministic and inspectable in the state dict.

## Worked example: the research workflow

Build it in the project (this is the multi-step orchestrator project's core): a four-stage workflow over the Nimbus corpus — `plan` (decompose the question into sub-queries), `retrieve` (per sub-query, access-filtered), `select` (composite selection per Chapter 11), `draft` (assemble per-stage context and answer with citations). Watch the per-stage context property: the `draft` stage's context contains the *selected* chunks from state, not the raw retrieval transcripts; the `retrieve` stage's context contains its sub-query and tool definitions, not the plan's prose. Then interrupt it after `retrieve` (checkpoint), bump a manifest version, and resume: the `select` stage runs against the new version's chunks — its state listed *ids and scores*, and ids re-resolve. The trace shows the skipped stages and the two that ran; the drift is absorbed invisibly. That invisible absorption is the whole point of the architecture.

## Exercises

1. **Beginner** — Build the research workflow's four stages and run two questions. Dump each stage's assembled context and mark, per stage: what would *not* have been there under transcript-handoff? What *fewer* things?
2. **Intermediate** — Add a fifth stage `verify` that checks the draft's citations against state's chunk ids. Now break the `select` stage deliberately (pick from an old version) and confirm `verify` catches it. Write one sentence on why verification must read from *state*, not from the draft's own context.
3. **Advanced** — Implement observation extraction: `retrieve` stores raw hits in a scratch dict, extracts `{chunk_id, score, heading}` to state, and drops the rest. Run a 20-question battery with and without extraction, and measure total tokens across the workflow from the allocation ledger. Report the savings and at least one question that got *worse* (an extracted-away detail that mattered).

## Common failures

- **The megatranscript.** Every observation carried forever; by step 8 the "context" is an archaeology dig with a small question appended. Extraction exists for this.
- **Decisions stored as prose.** State fields holding paragraphs instead of structured facts; later stages re-parse (fragile) or re-retrieve (wasteful). State should be the *conclusions*, not the conversation.
- **Checkpoint blindness.** Stages checkpointed, but resume tested never — then the first real crash reveals the checkpoint schema drifted from the stage's expectations. Resume tests are workflow tests (the suite shows the shape).
- **Unlabeled carryover.** Stage 3's summary entering stage 4's context as plain text — losing both provenance and the DERIVED label the auditor needs. Artifacts travel as components or they don't travel.

## Summary

- Agents re-decide context per step; naive loops drown in their own observations.
- State handoff beats transcript handoff: stages derive their own context, checkpoint only decisions, and resume absorbs drift by construction.
- Observations are extracted and summarized at the moment they arrive; raw payloads never cross stage boundaries twice.

## Mastery checklist

- [ ] I can build a stage workflow where each stage's context is visible and minimal, and defend each inclusion.
- [ ] I can demonstrate interrupt-version-change-resume absorbing drift, from a trace.
- [ ] I can implement observation extraction and quantify the token savings on a real battery.

## Review questions

1. Why does the orchestrator hand off *state* rather than *context* — and what specifically breaks in the replay alternative?
2. Why is "store the decision, not the observation" both a token policy and a correctness policy?
3. What is the relationship between per-stage checkpoints and Chapter 30's reliability stages (preview: idempotency)?

## References

- Anthropic, *Effective context engineering for AI agents* — compaction and structured note-taking as core agent operations — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (reviewed 2026-10-20)
- Yao et al., *ReAct* — the act-observe loop being managed — https://arxiv.org/abs/2210.03629 (reviewed 2026-10-20)
- Shinn et al., *Reflexion* — self-verification notes as agent context — https://arxiv.org/abs/2303.11366 (reviewed 2026-10-20)
- Implementation: `src/context_engineering/orchestrator.py`; tests `tests/unit/test_orchestrator.py`.

## Next

Chapter 22: multiple agents — when splitting the loop is worth it, and what isolation costs.

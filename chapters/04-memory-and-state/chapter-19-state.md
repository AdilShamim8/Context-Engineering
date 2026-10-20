# Chapter 19 — Structured State, Checkpoints, and Recovery

> Part IV · History, Memory, and State
> Prerequisites: Chapter 17 · Status: complete
> Time: ~50 minutes

## Overview

The third persistent thing is **task state**: not what was said (history) and not what the application remembered about the user (memory), but *where the work is* — steps done, decisions made, artifacts produced, what comes next. This chapter distinguishes the three precisely (teams conflate them into "the assistant's memory" at their peril), then builds checkpoints and resume on top: the ability to stop a multi-step task and continue later with the minimum reconstructable information. `history.py` and `memory.py` already carry the pattern (`to_state`/`from_state`); Part V's `orchestrator.py` operationalizes it per workflow stage.

## Context vs. memory vs. state: the three-column test

When you find yourself unsure which bucket something belongs in, apply the three questions:

| Question | History | Memory | Task state |
|---|---|---|---|
| Does it exist because it was *said*? | Yes | Maybe (user-stated) | No |
| Should it outlive the task? | No (summary only) | Yes | No — archived when done |
| Is it *produced by doing the work*? | No | No | Yes |
| Example | "the user asked about remote days" | "user's team is Platform-Reliability" | "steps 1–3 done; API spec drafted; next: verify auth" |

Why the separation matters: each artifact has different retention, different privacy rules (Chapter 25 cares), and different *reconstruction* semantics — the title of the chapter's second half. A "resume" that needs full history to work is a resume that breaks when history ages out; one that needs only state is robust to everything else expiring.

## Checkpoints: the minimum viable resume

A checkpoint is the serialized state needed to continue: **completed stage names, their outputs (or durable pointers to them), and the remaining plan.** What it explicitly is *not*: a dump of the assembled context, the history window, or the memory store. Those are reconstructible — context is rebuilt from state + stores by design (Chapter 17's statelessness point) — and stuffing them into checkpoints bloats storage, leaks data (Chapter 25: checkpoints are a persistence surface with retention obligations), and *breaks resume* when the world moved: the corpus version changed, the access policy changed, the model changed.

The design principle that follows: **checkpoints store decisions and pointers, never derived context.** Chapter 21's orchestrator will show the mechanism concretely — after each stage, it records `{"stage": name, "output": {...}}`; resume re-runs the pipeline from the first missing stage with the checkpointed outputs injected, rebuilding *fresh* context per stage (re-running access filters, re-checking versions) rather than replaying stale context.

## Recovery: the four interruption classes

1. **Process restart** (deploy, crash) — pure checkpoint resume; nothing else needed if state was durable.
2. **User pause/resume** ("continue this tomorrow") — checkpoint + history summary + a *resumption brief*: a DERIVED component that tells the model what it is resuming ("Task: migrate the API docs. Done: inventory. Current: auth section, 60%. Blocked on: nothing. Next step: draft.") The brief is what prevents the classic "resumed amnesia," where the model asks the user to re-explain what the logs show it already did.
3. **Failure recovery** (a stage failed; Chapter 30's retries exhausted) — checkpoint *before* failure is exactly what lets you retry the stage without redoing the plan. The degraded-mode ladder from Chapter 10 decides whether the task continues at reduced quality or halts for a human.
4. **External-world drift** (corpus updated mid-task) — the resume that re-derives context per stage is *correct by construction*: re-running version selection at resume means a policy that changed overnight is picked up automatically. Replayed stale context would carry yesterday's answer forward — Lab 00's failure with an extra step of indirection.

## Consistency: the state invariants

Three properties every state store must maintain, each enforced somewhere in this curriculum's code:

- **Complete resumability** — the state is sufficient to continue; the acid test is resuming with history and memory *empty*. (If resume needs anything not in the checkpoint, the checkpoint was a hope, not a state.)
- **Minimal footprint** — no context dumps, no copies of evidence (pointers to durable artifacts only), nothing sensitive that a summary would serve. Chapter 25: state is the *least* legitimate place for user data to accumulate.
- **Provenance continuity** — when checkpointed outputs become inputs to later stages, they carry their original sources; a resumed answer must still cite where its evidence came from, even across the restart.

## Worked example: resuming the migration task

State at interruption: `{"stages_done": ["plan", "retrieve"], "outputs": {"retrieve": {"chunk_ids": [...]}}, "next": "draft"}`. Resume: the orchestrator re-runs access filtering on the stored chunk ids (one was superseded overnight — the fresh version substitutes automatically), rebuilds the draft stage's context from the *new* chunk set, and the resumption brief orients the model. Compare the anti-pattern — checkpoint stored the assembled context text — which would have resumed drafting against the superseded policy, silently. Same interruption, same tools; one architecture resumes *correctly*, one resumes *confidently*. You know by now which of those two words the curriculum treats as the insult.

## Exercises

1. **Beginner** — Take any multi-step task you do and write its checkpoint schema: stage names, per-stage outputs (or pointers), remaining plan. Apply the acid test: could you resume it with no history and no memory? What's missing?
2. **Intermediate** — Build the resumption-brief generator: given a checkpoint, produce a DERIVED component (≤ 60 tokens) that orients a model to continue. Test: hand the brief + state to someone unfamiliar; can they continue the task correctly? (That is the real acceptance test for briefs.)
3. **Advanced** — Implement drift recovery: start a workflow over the corpus, change a manifest version mid-run, interrupt, resume. Prove from outputs that the resumed run used the new version, and write which stages *must* re-derive vs. which may legitimately use checkpointed outputs — with the reasoning.

## Common failures

- **The context-dump checkpoint.** Stores assembled context because "it worked"; breaks on drift, leaks on storage, and costs. State stores decisions and pointers.
- **Resumed amnesia.** Checkpoint exists but no resumption brief; the model re-asks questions whose answers are one log away. (Users read this as "it doesn't remember anything" — they are right.)
- **Infinite state.** Completed tasks' states archived forever, each a tiny privacy liability. State needs retention policy like everything else (Chapter 26).

## Summary

- Three artifacts, kept distinct: history (said), memory (remembered), state (working position) — different rules for retention, privacy, and reconstruction.
- Checkpoints store decisions and pointers; resume re-derives context per stage, which makes drift recovery correct by construction.
- The acid test of a checkpoint is resuming with everything else empty; the brief is what the model reads to *care* about resuming.

## Mastery checklist

- [ ] I can classify any persistent item into history/memory/state with the three-column test.
- [ ] I can design a checkpoint that passes the empty-everything acid test.
- [ ] I can explain why resume-rebuild beats replay in the corpus-drift scenario, and name which stages must re-derive.

## Review questions

1. Why does a context-dump checkpoint *break* resume (not just bloat it)?
2. What is in a resumption brief that is not in the state, and why does the model need both?
3. Which of the four interruption classes is *purely* a checkpoint problem, and what do the others additionally require?

## References

- Implementation pattern: `to_state`/`from_state` in `history.py`/`memory.py`; per-stage checkpoints in `orchestrator.py` (Part V).
- OpenAI, *Harness engineering* — durable task environments as agent infrastructure — https://openai.com/index/harness-engineering/ (reviewed 2026-10-20)

## Next

Part V: tools, multi-step workflows, and the agent-shaped uses of everything you just built.

# Chapter 30 — Reliable Context Pipelines

> Part VIII · Reliability, Performance, and Production
> Prerequisites: Part VII · Status: complete
> Time: ~55 minutes

## Overview

Reliability is the difference between a demo and a system: a pipeline that fails *predictably, gracefully, and loudly* where each failure mode demands it. This chapter assembles the reliability patterns around the machinery you already have — `pipeline.py`'s retries/fallbacks/required stages, `tools.py`'s guarded calls, `corpus.py`'s strict loader, `budget.py`'s loud overflow — and teaches the design decisions that bind them: modularity, validation, bounded execution, degradation ladders, and failure isolation.

## The reliability spine: five properties

1. **Modular stages with explicit interfaces.** The lifecycle's stages (Ch. 10) as named functions with payload-in/updates-out contracts. The payoff is *failure isolation*: when a stage dies, its neighbors keep working, tests keep passing, and the blame is one trace line away. God-functions — "build_context(question)" doing retrieval, selection, budget, assembly — are reliability debt: every failure is a full-pipeline failure, and no degradation ladder is possible because there is nowhere to stand.
2. **Validation at every boundary.** Manifest↔file agreement at ingestion (`corpus.py` raises — loud), argument schemas before tool execution (`validate_args`), and schema-shaped state between stages (Chapter 19's structured handoffs). The rule: garbage stops at the *boundary* it enters, never propagates to the stage that trusts it. Validation is also what makes retries safe — you cannot re-run a stage against data you never checked.
3. **Bounded execution everywhere.** Retries are capped (`retries=2` means three attempts, then a decision — never a loop); tool outputs are capped (`output_max_chars`); progressive disclosure gets a hop budget (Ch. 15); pipelines get stage counts. Unbounded anything — retries, recursion, result sets, context — is the reliability bug you meet at 3 a.m.
4. **The degradation ladder.** For each stage: what happens when it fails? Three answers, chosen by stage semantics: **fallback** (substitute behavior — empty evidence drives refusal semantics), **skip** (optional stage, degrade silently-but-visibly in the trace), **fail loud** (required stage: `StageError`; a corrupt budget must stop the request, because a silently-overflowed context is worse than an error). `tests/integration/test_pipeline_hardening.py` is the executable ladder — retrieval breaks → empty-evidence fallback; screening breaks → skipped; budget breaks → loud stop. Read it before designing yours.
5. **Loud beats silent.** The recurring decision: when in doubt, fail *loud*. Missing manifest file raises; unlisted files refuse to load; instruction overflow raises `BudgetError`. The silent failure in a context system doesn't stay contained — it becomes a wrong answer with a citation (Ch. 4's taxonomy, cost column).

## Retries, idempotency, and the "when it comes back" problem

Retries assume the *next* attempt can succeed — which requires stages to be **idempotent**: same inputs, same outputs, no partial side effects. Retrieval is naturally idempotent (read-only); *tool calls that write* are not, and Chapter 20's high-impact tools need human-in-the-loop or idempotency keys (the corpus's own API style guide mandates exactly this — fiction teaching production truth). Between retries, production adds **backoff** (exponential with jitter; the library's immediate retry keeps tests deterministic — the production pattern is a wrapper decision, not a library change, and Chapter 31 prices the tradeoff).

The second half of the problem is *what happens when the dependency stays down*: retries exhaust → fallback engages → the ladder continues. Design fallbacks as **quality floors, not improvisations**: empty-evidence fallback must produce refusal ("INSUFFICIENT CONTEXT"), not a guess; a degraded screener must tighten (treat unscreened content as blocked), not loosen. The rule to memorize: **degradation reduces capability, never safety** — a system that "recovers" by skipping the access filter did not recover.

## Failure isolation: blast radius as a design artifact

For each stage, ask: *if this corrupts its output, what else is poisoned?* The answers shape the design: structured payloads with schemas stop propagation at the next boundary; checkpointed workflows (Ch. 21) stop it at the next resume; per-call tool isolation (Ch. 20) stops it at the call. The audit question for review: which stages share mutable state? (The library's answer: none — payloads are copied per run, stages merge updates, state flows one direction. Keep it that way.)

## Worked example: designing the ladder for the capstone assistant

The capstone's stages with their reliability decisions, as a table you will imitate for your own systems:

| Stage | Failure mode | Behavior | Why |
|---|---|---|---|
| Load corpus | Missing file | Fail loud | Corrupt corpus must never serve answers |
| Retrieve | Index transient | Retry → empty fallback | No evidence → refusal, not crash |
| Version filter | Manifest inconsistent | Fail loud | Stale-vs-current is correctness, not availability |
| Access filter | Policy unparsable | Fail loud | Authorization never degrades (Ch. 24) |
| Screen | Screener timeout | Skip + treat unscreened as blocked | Detection is best-effort; *blocking* is the floor |
| Budget | Estimator failure | Fail loud | Silent overflow is the worst outcome |
| Assemble | Any failure | Fail loud | The request is the product; never ship malformed |
| Respond | Responder exception | Fail loud with clean message | No fabricated answers on the error path |

Notice the asymmetry: availability stages degrade; correctness and safety stages stop. That asymmetry *is* the design — a ladder that only ever degrades eventually degrades something that should have stopped the train.

## Exercises

1. **Beginner** — Extend the hardening test with two new broken stages of your choosing and predict the trace before running. Verify.
2. **Intermediate** — Implement the backoff wrapper: a `with_backoff(fn, base_ms, jitter)` utility that wraps stage functions for production use while keeping a no-delay path for tests. Write the test that proves both modes and the bound (max attempts × max delay).
3. **Advanced** — The poison-pill drill: make `retrieve` return malformed evidence ids (wrong type) and watch the failure surface where validation should be — then add the boundary validation that stops it at `select`, and at `budget` as defense in depth. Report the two trace lines that changed, and argue which single boundary would have sufficed (and why the answer is "both" in production).

## Common failures

- **The god-function.** One function, every failure global. Stages exist so failures can be local.
- **Infinite optimism.** Unbounded retries on a dependency that is down *hard*; the queue grows, the latency compounds, the incident doubles. Bounded retries + fallback + alert is the professional pattern.
- **Degrading the wrong thing.** Fallbacks that skip access control or validation to "keep the system up." Degradation reduces capability, never safety — engrave it.
- **Silent partial state.** A stage that half-writes its output then fails; the next stage reads the half. Schemas + fail-loud stop this class.

## Summary

- Modular stages, boundary validation, bounded everything, and a degradation ladder whose asymmetry is deliberate: availability degrades, correctness and safety stop.
- Idempotency gates retries; fallbacks are quality floors; blast radius is designed, not discovered.
- Loud beats silent — the recurring verdict of every chapter since 4.

## Mastery checklist

- [ ] I can write the ladder table for any pipeline I design, with a why per row.
- [ ] I can implement bounded retries with a backoff wrapper and test both paths.
- [ ] I can trace a poison-pill failure through boundaries and argue the validation placements.

## Review questions

1. Why does the empty-evidence fallback produce refusal rather than a "best-effort" answer — what principle does that encode?
2. What makes a stage idempotent, and why is idempotency a precondition for retrying it?
3. Give one stage from the worked table where "skip" would be correct, and explain what its absence from the table's skip rows would cost.

## References

- Implementation: `pipeline.py`, `tests/integration/test_pipeline_hardening.py`; boundary examples across `corpus.py`, `tools.py`, `budget.py`.
- OWASP LLM Top 10 — "unbounded consumption" and availability categories — https://owasp.org/www-project-top-10-for-large-language-model-applications/ (reviewed 2026-10-20)

## Next

Chapter 31: the same system, priced — performance, cost, and the trade-off discipline.

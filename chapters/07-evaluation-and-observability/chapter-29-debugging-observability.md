# Chapter 29 — Context Debugging and Observability

> Part VII · Evaluation, Testing, and Observability
> Prerequisites: Chapters 27, 28 · Status: complete
> Time: ~55 minutes

## Overview

Observability is Chapter 4's diagnostic loop made durable: when something goes wrong in production, you must be able to answer "what did the pipeline actually do?" from stored, redacted, stage-level evidence — without reproducing the failure or arguing from memory. This chapter builds the trace model (`observability.py`), the operational metrics that matter, the redaction-first rule that keeps observability from becoming a liability, and walks a full debugging session from trace to root cause.

## The trace: structure, never content

`ContextTrace` records what each stage did — name, outcome, duration, tokens in/out, dropped ids, scalar notes — and *by design* never stores payload content. The reasoning is Chapter 25's: the assembled request is the most sensitive artifact in the system; a trace that archives it is a data warehouse of user content wearing a debugging costume. The pattern that survives an audit:

```
STAGE              OUTCOME       MS   TOK_IN  NOTES
retrieve           ok         0.412      10  hits=6; query_tokens=10
screen             ok         0.108      68  findings=1; policy=flagged
select             ok         0.203      68  selected=3; dropped=ev-remote-v1-stale
budget             ok         0.141     231  truncated=1; allocated=189
assemble           ok         0.087     189  tokens_out=189
answer             ok         0.014     189  status=answered
```

Every number there answers a Chapter 4 diagnostic question: was evidence found (`hits=6`), did screening flag something (`findings=1`), did the *right* thing get dropped (`dropped=...v1-stale` — ids, never text), what did budget take (`truncated=1`)? Redaction still applies to notes by default — the day a teammate stuffs an email into a note, the trace renders `[REDACTED:email]` — because observability code must assume its own mistakes.

## The metrics that matter operationally

Four families, all derivable from what the stack already emits:

1. **Latency, per stage.** From trace durations: p50/p95 per stage *and* per pipeline. Stage-level latency is how you know the budget grew a tumor in `select` or retrieval regressed — a single end-to-end number tells you *that* you're slow; stage numbers tell you *who*.
2. **Token usage.** Per request (allocation report) and per kind (instructions vs. evidence vs. history drift — Chapter 17's cost story as a dashboard). Trends here are cost regressions *and* quality regressions: history share creeping upward is the unbounded-window failure arriving in slow motion.
3. **Failure rates, by stage and type.** From trace outcomes: `failed` counts per stage, `fallback` counts (degradation happening — visible or not?), `dropped` component counts. Distinguish *crashes* (rare, loud) from *degradations* (common, silent) — the second is where quality leaks.
4. **Retrieval and selection behavior.** Hits per query (bimodal distributions = vocabulary mismatch, Chapter 8), scores' spread (collapsed scores = ambiguous queries), dropped-but-relevant (needs Chapter 27's level-2 metrics). These are the early-warning family: quality drops show here *before* users notice answers.

The anti-metric to name explicitly: **answer-level "quality scores" from the pipeline itself** (self-graded confidence). Track if you must; never gate on it; it measures the model's self-image, not the outcome. Grounding metrics (Ch. 27) are the honest version.

## Redaction-first, as a habit

Three rules, enforced by this repository's code and worth enforcing in yours:

1. **Traces store structure, not content** — ids, counts, labels; the content lives in its source of truth and is re-fetchable when a human investigates.
2. **Redaction applies by default, at write time** — not "we'll scrub before export" (nobody does), but at `render()` — the `security.redact` call in the trace pipeline is the pattern.
3. **Access applies to observability data too.** Traces inherit the sensitivity of what they describe; a trace about a restricted-document query is itself restricted (Chapter 25's exposure budget, applied to the debugging plane).

## Worked example: a full debugging session

Symptom (from the golden suite, in CI): gc-01 fails with "missing required fact: '2 days'". The debugging loop, using only stored evidence:

1. **Dump the request trace** for the failing case. `retrieve: hits=6` — evidence was found. `select: dropped=hr-remote-work-v1-c01` — wait, *stale* v1 was dropped... but the answer still lacks "2 days".
2. **Check the assembly.** `budget: truncated=1` — something got cut. The allocation report (level-3 artifact) says `ev-remote-work-v2-c01  truncated 132/590`. The *policy chunk with the answer* was truncated.
3. **Correlate.** The test recently added a large history fixture to the bundle; instructions + history now consume the budget before the evidence (Chapter 12's worked example, happening live). Root cause: **priority change in the fixture** — history at priority 1 now outranks evidence at 2.
4. **Fix by policy, not by patch.** Either restore evidence priority or compress history (Chapter 14 before the allocator, not truncation inside it). Fix, re-run: green.
5. **Add the regression case** — a golden variant with the big history bundle — so the same priority inversion can never land silently again (Chapter 28).

Total time: minutes, with evidence at every step. Without the trace: an afternoon of print statements and "works on my machine." That difference *is* the observability investment.

## Exercises

1. **Beginner** — Instrument the golden-suite pipeline with `ContextTrace` stages and render a trace for one question. Annotate each line with the Chapter 27 level it observes.
2. **Intermediate** — Build the metrics extract: from a batch of traces, compute p50/p95 per stage and the truncation/fallback rates. Run the suite 5× and report which metric is *noisiest* — then decide (in writing) whether that noise is worth alerting on.
3. **Advanced** — The counterfactual debugging drill: break the pipeline in three specific ways (drop the version filter; swap a priority; un-pin a constraint) and for each, identify *which single trace line* reveals it. The deliverable is the three-line "signature table" — your system's field guide.

## Common failures

- **Content dumps.** Traces storing assembled requests "for completeness" — the surveillance trap (Ch. 25/26); structure re-fetches content when needed.
- **Latency without stages.** One end-to-end number; every regression is a mystery. Per-stage timings cost nothing and name suspects.
- **Alerting on noise.** Alerting on the noisiest metric trains the team to ignore alerts; Chapter 31's method (measure, then decide) applies to observability itself.
- **Unredacted exports.** The "we'll scrub later" pipeline; later never comes. Redact at write time, by default, in code.

## Summary

- Traces: structure, never content; ids, counts, durations, decisions — redacted at write time.
- Four metric families: per-stage latency, token usage by kind, failure/degradation rates, retrieval/selection behavior — all from existing artifacts; self-graded quality is the anti-metric.
- Debugging becomes evidence-driven: trace → correlate with allocation/selection artifacts → policy fix → regression case.

## Mastery checklist

- [ ] I can instrument a pipeline with stages and explain what each trace line rules in/out diagnostically.
- [ ] I can extract the four metric families from a batch of traces and say which are alert-worthy and why.
- [ ] I can run the three-way signature drill and identify each planted failure from one trace line.

## Review questions

1. Why is a stage-level `dropped=[ids]` line diagnostic gold while a stored payload would be a liability?
2. Which two metric families give earliest warning of quality (not just performance) regressions?
3. Why is "self-graded confidence" an anti-metric — what does it measure instead of quality?

## References

- Implementation: `src/context_engineering/observability.py`; `tests/unit/test_observability.py`; the worked session replays `tests/evaluation/test_golden_suite.py`.
- OWASP LLM Top 10 — sensitive-disclosure categories that redaction-first exists to prevent — https://owasp.org/www-project-top-10-for-large-language-model-applications/ (reviewed 2026-10-20)

## Next

Part VIII: taking the stack from "works and measured" to "reliable, economical, and maintained."

# Chapter 27 — Measuring Context Quality

> Part VII · Evaluation, Testing, and Observability
> Prerequisites: Part III · Status: complete
> Time: ~70 minutes

## Overview

"Does it work?" is not one question, and the industry's habit of answering it with a single vibe-number is how teams ship systems they cannot improve. This chapter establishes the evaluation model the rest of Part VII runs on: **six quality levels, deliberately not interchangeable**, each with its own metrics, its own failure stories, and its own owner. Then it builds the first level practically: the golden-case harness (`evaluation.py`) that scores grounded answers, and the metric families you will extend as the curriculum's systems grow.

## The six levels (and why they are not interchangeable)

| Level | Question it answers | Typical metric | Failing level looks like |
|---|---|---|---|
| 1. Retrieval quality | Did we FIND the right content? | Recall@k, precision@k vs. known-relevant ids | "The answer was out there; we never saw it" |
| 2. Selected-context quality | Did we KEEP the right content? | Coverage of required facts, redundancy ratio, diversity | "We found it, then deduped/diversity-dropped it" |
| 3. Assembly quality | Did the right content SURVIVE assembly in usable form? | Allocation report deltas, truncation hits, label correctness | "It was selected, then truncated mid-fact or buried" |
| 4. Memory quality | Did we remember/retrieve/update the right facts? | Extraction precision, conflict rate, TTL correctness | "Wrong or stale memory silently winning" |
| 5. Response quality | Did the model USE the context correctly? | Fact coverage in answer, citation correctness, hallucination rate | "Right context, wrong or invented answer" |
| 6. End-to-end task success | Did the USER's job get done? | Task completion, latency, cost, user corrections | "Good answers, useless product" |

The interlocking failure this table prevents: a team measures level 6 (or worse, a demo), sees 80%, and iterates on prompts — while the actual defect is level 1 (recall) or level 3 (truncation). **Each level has its own instruments**; `evaluation.py` measures level 5 (grounding) with golden cases whose failures *name their level* — "missing required fact" is a grounding failure; "expected source not cited" points upstream at 1–3; "answered instead of refusing" is an access/sufficiency failure (Chapters 9, 11). The report's guidance block exists to stop the reflex of reading any failure as "model bad."

## Golden cases: the fixture pattern that scales honestly

A golden case is the smallest honest unit of evaluation: input + expected grounding behavior. The suite in `datasets/synthetic/golden/golden_cases.json` shows the full grammar in 12 cases: ordinary facts, numbers, **version conflict** (stale v1 must not win), **access control** (refusal for general users, correct answer for authorized), **no-evidence refusal** (the system must be allowed to say "insufficient"), and **injection-fixture non-participation** (forbidden content). Three design decisions matter more than the count:

1. **Cases are data, not code** — reviewable in one file, versionable with the corpus (`corpus_version` field), and extendable without touching the harness. Chapter 28's staleness detection keys on that field.
2. **Refusal is a first-class expected behavior.** Suites that only test "answered correctly" train systems that never shut up; ours tests that wrong answers are *refused* and restricted ones are *not guessed at*.
3. **Required facts over full-text matches.** `required_facts` are the facts that must appear (numbers, phrases) — not a fragile exact-answer string. For deterministic systems this is strict; for model-backed systems it survives paraphrase.

The harness's independence contract: `run_suite(cases, pipeline_fn)` — anything that answers `{"answer_text", "citations"}` can be evaluated. The deterministic chain and a real model are the same shape to this code, which is why Chapter 35's assistant plugs in without harness changes.

## The metric families, level by level

Beyond the harness's grounding metrics, each level has instrument families you can now build on the existing library:

- **Retrieval (1):** known-relevant chunk ids per question → recall@k, precision@k. You have everything: `LexicalIndex.search` returns ids; fixtures declare relevance.
- **Selection (2):** required-fact coverage of selected chunks *before* answering; redundancy ratio (pairwise Jaccard among selected); dropped-but-relevant count (the diversity bug catcher).
- **Assembly (3):** from `AllocationResult`: truncation count per component, dropped ids vs. relevant ids, token totals per kind. The allocation report *is* an assembly-quality metric stream.
- **Memory (4):** extraction precision (proposed memories a human marks correct), conflict rate, TTL-expiry correctness — `memory.py`'s audit trail is the raw data.
- **Response (5):** what the harness does: fact coverage, citation correctness, forbidden-content absence, refusal correctness.
- **End-to-end (6):** wall-clock latency (`observability.py` gives per-stage timing), tokens (`budget.py` gives per-request totals), cost (tokens × price — a config, not a mystery), and task completion on scripted scenarios.

## Worked example: reading a failing report as a map

Run the suite against the deterministic pipeline with selection diversity *disabled* (the ablation from Chapter 28's lab). Two classes of failure appear: carryover-style questions lose the second relevant chunk (diversity would have kept it — level 2), while conflict questions still pass (version selection is upstream of diversity — unchanged). Now disable current-version filtering *instead*: gc-01 fails with *forbidden* content ("3 days") present — a level-1/2 failure with a different signature (wrong version retrieved, not wrong ranking). Same pass-rate drop (~1 case), completely different diagnosis, completely different fix. **This is the argument for level-attributed metrics: the pass rate told you nothing; the failure signatures told you everything.**

## Exercises

1. **Beginner** — Extend the golden suite with two new cases of your own design (one edge case, one ordinary). Run them against the deterministic pipeline before and after adding them; report what drafting the cases taught you that reading the suite did not.
2. **Intermediate** — Implement level-2 metrics: for each golden case, compute required-fact coverage over *selected* chunks (before answering) and redundancy ratio among them. Report the two cases with the worst coverage and the one with the worst redundancy — and state which level each belongs to.
3. **Advanced** — Build the six-level dashboard for the curriculum's stack: one metric per level, all from existing artifacts (trace, allocation report, selection metadata, harness results). Run the full suite once and annotate each metric with its level and its failure story. The deliverable is the annotation, not the dashboard.

## Common failures

- **The single-number system.** One aggregate score; improvement is indistinguishable from noise; failures are undiagnosable. Six levels, six instruments.
- **Test-the-demo suites.** Golden cases written by copying the system's current outputs — enshrining bugs as truth. Cases are written from the *corpus and policy*, never from the system's answers.
- **Refusal-blind suites.** Every case expects an answer; the system learns to always answer; Chapter 11's "insufficient" and Chapter 9's access refusals go untested.
- **Metric worship at one level.** Perfect recall@10 (level 1) celebrated while level 3 truncates the winners mid-sentence. Levels trade off; you must see the trade.

## Summary

- Six quality levels, not interchangeable, each with its own metrics and failure stories; the harness's failure messages name their level.
- Golden cases are data: refusal and conflict and access behaviors as first-class expectations, versioned with the corpus.
- The deterministic stack is fully instrumentable today — every level has an artifact stream you can metric.

## Mastery checklist

- [ ] I can name the six levels from memory and give each one failure story + metric.
- [ ] I can read a harness failure and attribute it to a level before proposing a fix.
- [ ] I can write a golden case whose expected behavior comes from the corpus, not from the system.

## Review questions

1. Why does "expected source not cited" point *upstream* of level 5, and to which levels exactly?
2. What makes a refusal-testing case different in kind from an answer-testing case, and what behavior does its absence train?
3. Which level does redundancy-ratio measure, and which bug class does it catch that recall cannot?

## References

- Implementation: `src/context_engineering/evaluation.py`; suite: `datasets/synthetic/golden/golden_cases.json`; end-to-end runner: `tests/evaluation/test_golden_suite.py`.
- Liu et al., *Lost in the Middle* — why level 3 (position) is a real level, not a refinement — https://arxiv.org/abs/2307.03172 (reviewed 2026-10-20)

## Next

Chapter 28: the discipline around these instruments — test-driven context engineering, ablations, and regression suites.

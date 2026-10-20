# Chapter 28 — Test-Driven Context Engineering

> Part VII · Evaluation, Testing, and Observability
> Prerequisites: Chapter 27 · Status: complete
> Time: ~65 minutes

## Overview

Chapter 27 built the instruments; this chapter is the discipline of using them: **change one thing, measure, keep or revert.** It covers the test-first habit for context systems, ablations that attribute quality to components, regression suites that gate corpus and config changes, and the honest handling of the parts that cannot be deterministic (model-dependent behavior). The curriculum itself is the case study: every module you have read shipped with its tests in the same commit, and every golden case pins a behavior the earlier chapters promised.

## The deterministic-first testing rule

The rule the whole repository runs on: **deterministic components get deterministic tests; model-dependent behavior gets protocols and labeled evidence, never fake certainty.** Concretely:

- Budgeting, selection, access filtering, version selection, security screening, memory TTL, conflict flags, trace redaction — all deterministic, all unit-tested, all edge-cased. If a change breaks them, the suite says *which line of policy* broke.
- Retrieval is deterministic *given* the corpus (BM25 is math, not magic) — so corpus changes are test events (below).
- Answer *quality* through a real model is not deterministic — so it is evaluated by golden cases that check *grounding* (facts present, sources cited, refusals honest) rather than exact strings, and, when a real model is wired in, by repeated runs with reported variance, never by a single lucky sample.

The failure mode this rule prevents is the industry's default: "we tested it manually with three questions" — three questions whose luck became the team's definition of correctness.

## Ablations: attribute quality to components

An ablation answers "what does this component actually contribute?" by removing it and measuring. `evaluation.ablate(cases, baseline_fn, variants)` runs the suite under the baseline and under named variants; the deliverable is **case-level deltas, not aggregate deltas** — the worked example in Chapter 27 showed two ablations with nearly identical pass-rate impact and completely different failure signatures.

The ablation discipline, worth writing on the wall:

1. **One variable per variant.** "No-diversity AND no-version-filter" tells you nothing about either.
2. **Name the hypothesis before running.** "Diversity contributes on multi-facet questions (gc-04, gc-06); no effect elsewhere." Falsifiable beats vibes.
3. **Read the failures, not the rate.** Which *cases* changed and *how* is the finding; ±1 in the aggregate is noise looking for a narrative.
4. **Ablate before adding, too.** The Chapter 8 four-question justification is the pre-implementation ablation: what measured failure does this new stage fix? "It scored better when we added it" without an ablation of what it displaced is how pipelines accrete.

## Regression suites as gates: corpus changes are code changes

The golden suite's `corpus_version` field makes corpus evolution testable. The working flow, demonstrated by the curriculum's own tests: bump a manifest version → `select_current_versions` changes → conflict cases (gc-01) and citation expectations re-run → if a fact moved (carryover cap 5 → 6 days), the golden case *fails on the old fact* and the fix is updating the case in the same commit as the corpus change. Three properties fall out:

1. **Staleness detection is automatic.** Cases pinning facts the corpus no longer contains fail loudly instead of silently testing the wrong world.
2. **The commit is the review unit.** Corpus edit + manifest bump + golden-case update + test run in one reviewable change — the reviewer sees intent, mechanism, and evidence together.
3. **CI-able without services.** The whole suite runs offline in milliseconds; there is no environment excuse for not gating every change (the owner may add a CI runner later; ROADMAP.md tracks it).

## Adversarial and edge cases as first-class citizens

The suite demonstrates the categories that teams systematically forget:

- **No-evidence** (gc-10): the system must refuse — testing the *negative* space is what makes refusal behavior real.
- **Conflict** (gc-01): two versions exist; only the current one may win; the forbidden list catches the stale number.
- **Authorization boundaries** (gc-07/08/09): refusal for the general user, *correct answer* for the authorized user — a pair, because testing only refusal trains systems that over-refuse, and testing only answers leaks.
- **Injection adjacency** (gc-06's forbidden list): the payload lives in a document that must still be *usable* (refund policy!) while never *winning*.
- **Numbers and formats** ("1,500", "team.feature.description"): exact-value cases catch compression loss (Ch. 14) and normalization damage (Ch. 6) that prose checks slide past.

## The model-dependent protocol (for when a real model joins)

When you wire a real model behind the harness's `pipeline_fn`, four rules keep the results honest: (1) run *n* ≥ 3 repeats and report means *and spread* — a single sample is weather, not climate; (2) keep golden-case grounding checks (facts/citations/refusals), add exact-string checks *never*; (3) pin the model version and record it — model updates are regression events (Chapter 32); (4) keep the deterministic suite as the fast gate and the model suite as the expensive one — never let the expensive suite be the only one.

## Exercises

1. **Beginner** — Write one golden case per category above for a corpus of your own (or the Nimbus one): one no-evidence, one conflict, one authorization pair. Note which category you found hardest to write — that's your team's next incident.
2. **Intermediate** — Run the Chapter 27 worked example yourself: ablate diversity, then current-version filtering, on the golden suite. Produce the case-level delta table and the two diagnoses. Confirm (or refute) the claim that aggregate rates hide the difference.
3. **Advanced** — Build the gating workflow: a script that runs unit + integration + golden suites and *refuses to proceed* on failure (exit codes), plus a `--changed-corpus` mode that re-runs and reports which golden cases pin stale facts. Use it to make a corpus edit (bump `hr-vacation` to v4 in a scratch copy) and walk the full flow: edit → fail → case update → pass.

## Common failures

- **Fixture theater.** Cases written from the system's outputs (circular validation); every bug becomes a specification. Write from the corpus.
- **Aggregate-worship.** Reporting pass rates without reading failures; regressions and improvements become indistinguishable.
- **The unversioned suite.** Cases aging with the corpus silently, testing last year's facts — the `corpus_version` field and stale-fact detection are the antidote.
- **Ablation theater.** Multi-variable "ablations" that confirm whatever was already believed. One variable, named hypothesis, case-level reading.

## Summary

- Deterministic-first: everything testable deterministically is; model-dependent behavior gets protocols with variance, versioning, and grounding-level checks.
- Ablations attribute quality to components: one variable, named hypothesis, case-level deltas.
- Corpus changes are code changes: manifest + cases + tests move together, gated by an offline suite that has no excuse not to run.

## Mastery checklist

- [ ] I can run and author golden cases across all edge categories, writing expectations from the corpus.
- [ ] I can design a one-variable ablation with a falsifiable hypothesis and read its case-level table.
- [ ] I can execute the corpus-change gating flow end-to-end, including the stale-fact update.

## Review questions

1. Why do authorization cases come in refusal/answer *pairs* — what does each half alone train?
2. Why are case-level deltas more informative than aggregate deltas in an ablation? Give the mechanism, not the slogan.
3. What exactly does `corpus_version` gate, and what failure does its absence cause?

## References

- Implementation: `evaluation.ablate`, `run_suite`; suite runner `tests/evaluation/test_golden_suite.py`.
- Asai et al., *Self-RAG* — adaptive behavior that itself needed ablation-driven evaluation — https://arxiv.org/abs/2310.11511 (reviewed 2026-10-20)

## Next

Chapter 29: debugging with the instruments — traces, metrics, and the redaction-first habit.

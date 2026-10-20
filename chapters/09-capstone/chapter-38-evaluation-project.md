# Chapter 38 — Advanced Context Evaluation Project

> Part IX · Integration and Capstone
> Prerequisites: Part VII · Status: complete
> Time: ~120 minutes (project time)

## Overview

The evaluation harness is where the curriculum's authority comes from — and this chapter is its full-strength exercise: **comparing multiple context strategies as a research project, with a documented dataset, reproducible runs, and a report that names its own limitations.** The deliverable is not "my variant won"; it is an evidence pack a skeptical engineer would accept. The project spec lives at `projects/advanced/context-evaluation-harness/`; this chapter frames the research posture.

## The experiment set (minimum viable study)

Four comparisons, each one-variable, each against the 12-case golden suite (extended with your own cases by now):

1. **Selection width**: max_items ∈ {4, 8, 12} — the coverage/cost knee (Ch. 11/31).
2. **Diversity on/off**: the redundancy/coverage trade (Ch. 11).
3. **Compression-before-budget on/off**: the truncation/prevention trade (Ch. 14/12).
4. **Current-version filtering on/off**: the conflict-resolution backstop (Ch. 9) — expected to fail exactly gc-01; a one-case, high-signal "policy proof" run.

The report structure that makes it a *study* rather than a demo: for each comparison — hypothesis (written first, per Ch. 28), case-level delta table, three-metric columns (correctness, tokens, latency), the verdict, and **the limitation paragraph**: what this suite cannot see (model-dependent effects — the deterministic responder measures mechanics, not attention), what n=1 corpus means, and what would change at 10× scale. The limitations section is not boilerplate; it is the difference between an engineer and an enthusiast.

## The artifacts this study produces

- **The matrix**: variant × case, failures named per Chapter 27's levels.
- **The knee plot**: coverage vs. tokens for comparison 1, with your chosen default marked and justified.
- **The one-case proof**: comparison 4's single failure, annotated as *intended behavior* — the strongest kind of test evidence: the system failing in exactly the way its policy says it must.
- **The limitations paragraph**, honest about the deterministic boundary.

## Exercises (the project IS the exercise set — see the spec for full requirements)

1. **Beginner** — Run comparison 4 (version filtering off) and write the one-page analysis of its single, policy-predicted failure. Attach the trace.
2. **Intermediate** — Run comparisons 1–3, produce the matrix and knee plot, and write the shipping recommendation with the two failure cases each rejected variant would introduce.
3. **Advanced** — Extend the study with one *model-dependent* protocol (optional adapter; Ch. 28's rules): repeat runs with variance on the grounding metrics, and report how the deterministic conclusions hold or soften.

## Mastery checklist

- [ ] I can produce a one-variable study whose tables, plots, and verdicts are all reproducible from my commands.
- [ ] I can write the limitation paragraph that a reviewer reads and believes.
- [ ] I can name which of my findings generalize (policy/structure) and which are corpus-specific (parameters).

## Next

Chapter 39: the final capstone — your system, your evidence, your defense of both.

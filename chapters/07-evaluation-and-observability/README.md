# Part VII — Evaluation, Testing, and Observability

> Chapters 27–29 · Prerequisites: Part III · Outcome: a system whose quality is measured at six levels, whose changes are gated by evidence, and whose failures are debugged from traces.

## Chapters

| # | Chapter | Focus | Code |
|---|---|---|---|
| 27 | [Measuring Context Quality](chapter-27-measuring-quality.md) | Six levels; golden cases; metric families | `evaluation.py` |
| 28 | [Test-Driven Context Engineering](chapter-28-test-driven.md) | Ablations, regression gates, corpus-as-code | golden suite |
| 29 | [Context Debugging and Observability](chapter-29-debugging-observability.md) | Structure-not-content traces; the four metric families | `observability.py` |

## The part's single idea

**"Does it work?" is six questions, and each has its own instrument.** The golden suite scores grounding with level-attributed failures; ablations attribute quality to components; traces turn debugging from archaeology into evidence review. When something regresses, you don't ask "what changed in the vibe" — you run the suite, read the failure's level, and look at the trace line that names the stage.

## Completion criteria

- [ ] You can write golden cases (all edge categories) from the corpus, not from system outputs (Ch. 27).
- [ ] You can run a one-variable ablation and read its case-level deltas as a diagnosis (Ch. 28).
- [ ] You can debug the worked session from trace + allocation report, and add the regression case that locks the fix (Ch. 29).

Next part: [Part VIII — Reliability, Performance, and Production](../08-production-engineering/).

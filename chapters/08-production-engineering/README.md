# Part VIII — Reliability, Performance, and Production

> Chapters 30–33 · Prerequisites: Part VII · Outcome: the stack survives contact with production — failing predictably, priced honestly, released coherently, and compared on evidence.

## Chapters

| # | Chapter | Focus | Code |
|---|---|---|---|
| 30 | [Reliable Context Pipelines](chapter-30-reliable-pipelines.md) | Modularity, validation, bounded execution, degradation ladders | `pipeline.py`, hardening tests |
| 31 | [Performance, Cost, and Scalability](chapter-31-performance-cost.md) | Four cost centers; the levers and their trades; knee-finding | ledger + traces |
| 32 | [Deployment, Monitoring, and Maintenance](chapter-32-deployment.md) | The four-way version tuple; regression gates; rollback | manifest + suite |
| 33 | [Provider and Framework Comparisons](chapter-33-provider-comparisons.md) | Eight criteria; baseline-first; dated claims | method |

## The part's single idea

A context system is four evolving inputs — code, corpus, config, model — held coherent by **evidence gates**: every change class (including corpus and config, which most teams treat as weather) runs the same suite, ships in the same reviewable units, and rewinds as one tuple. Reliability is the ladder's deliberate asymmetry (availability degrades, correctness stops); economics is the three-metric comparison (correctness, latency, tokens) applied to every lever; ecosystem decisions are Chapter 28's ablation discipline pointed outward.

## Completion criteria

- [ ] You can write and test a degradation ladder, including which stages must fail loud and why (Ch. 30).
- [ ] You can produce a three-metric variant comparison and find a lever's knee (Ch. 31).
- [ ] You can execute the corpus-release runbook end-to-end with its golden-case gate and rollback rehearsal (Ch. 32).
- [ ] You can fill the eight-criteria table with evidence and write an adoption memo that cites it (Ch. 33).

Next part: [Part IX — Integration Projects and Capstone](../09-capstone/).

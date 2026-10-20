# Chapter 39 — Final Context Engineering Capstone

> Part IX · Integration and Capstone
> Prerequisites: All parts · Status: complete
> Time: open-ended (the portfolio piece)

## Overview

The final capstone is yours to define, within a frame that forces integration of the whole curriculum: **design and build a complete context-aware application — on a new domain you choose — with a defensible architecture, meaningful evaluation, documented trade-offs, and real security and reliability measures.** The Nimbus corpus and the library stay available as a foundation; the *new* content (corpus, policies, golden cases) is your own synthetic invention. The deliverable is an evidence pack, not a demo.

## Requirements (the frame)

1. **A new governed domain.** A synthetic corpus (≥8 documents, ≥2 access classes, ≥1 superseded version, ≥1 known conflict, ≥1 access-control refusal scenario) with a manifest, strict loading, and current-version selection. Reuse the governance pattern; invent the world.
2. **The full request path.** Access-filtered retrieval, screening, composite selection, budgeted assembly with labels, citation-bearing answers, honest refusal. (You have done this once; the second time is where the learning consolidates — expect your Chapter 34 porting instincts to fire.)
3. **At least one extension beyond the knowledge assistant** — pick where your domain needs it most: memory (Ch. 18), multi-step workflow with checkpoints (Ch. 21), progressive disclosure (Ch. 15), or history with pinned constraints (Ch. 17). One, done deeply with its tests, beats three done shallowly.
4. **A golden suite** (≥10 cases) covering all five behavior categories from Chapter 28 — ordinary, conflict, no-evidence, authorization-pair, injection-adjacency — versioned with your corpus.
5. **One ablation with a written hypothesis**, run honestly (Ch. 38's posture), verdict included even when it refutes you.
6. **A security posture write-up**: the layered-defense table filled for *your* system, with the tests that pin each layer (Ch. 24).
7. **The architecture brief**: components kept/replaced/extended from the reference library, with reasons (Ch. 34's advanced exercise, now for real).

## The defense (the true deliverable)

The capstone ends with a defense, because that is how engineering is actually evaluated: **a 30-minute walkthrough where a skeptical reviewer (a peer, a mentor, you-in-six-months) picks any behavior and asks "show me."** Show, from your own artifacts: the trace for that request, the golden case that pins it, the ablation that priced it, the security test that contains its failure mode. The repository you have built IS the defense — if every question resolves to an artifact in seconds, you have finished this curriculum; if some resolve to "probably," those are your next iterations, and you now know exactly how to run them.

## Grading rubric (how "done" is judged)

| Dimension | Excellent | Passing | Failing |
|---|---|---|---|
| Governance | Manifest complete, tests enforce it | Fields present, some tests | Metadata theater |
| Correctness | Suite green, refusal-pairs pinned | Suite green, thin categories | Cases copied from system outputs |
| Security | Layer table + tests per layer | Posture described | "The prompt says don't" |
| Evaluation | Ablation with honest verdict | Metrics present | Aggregate scores only |
| Architecture | Keep/replace reasons per component | Reuse without reasons | God-function rebuild |
| Defense | Any question → artifact in seconds | Most questions resolve | Hand-waving |

## Exercises

1. The capstone is the exercise. Scope it to two weekends: weekend one, corpus + policies + path + suite; weekend two, the extension + ablation + write-ups + defense rehearsal.
2. If you want the collaborative version: trade capstones with another learner and run each other's defenses — the reviewer who breaks your system does you the favor this curriculum was built around.

## Mastery checklist — the curriculum's final version

- [ ] I can build a governed corpus and full request path in a new domain without re-reading the chapters.
- [ ] I can produce an evidence pack (suite, ablation, security tests, traces) that survives hostile review.
- [ ] I can defend any behavior of my system from artifacts, in seconds, and name my system's honest limitations unprompted.

That last checkbox is the definition of a context engineer this curriculum was aiming at. Everything else was scaffolding for it.

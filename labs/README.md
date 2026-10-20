# Labs

Guided, verifiable exercises tied to chapters. Every lab is deterministic and offline unless explicitly marked otherwise. Prediction-first is the standing rule: write your prediction, run, reconcile — miscalibration is the learning signal, not a score to hide.

| Lab | Time | Chapters | Focus |
|---|---|---|---|
| [Lab 00 — First Context Experiment](lab-00-first-context-experiment/) | ~30 min | 0.3 | The thesis observed: context determines the answer, including confident-and-stale |
| [Lab 07 — Chunking and Retrieval Experiments](lab-07-chunking-and-retrieval/) | ~45 min | 7, 8 | Parameter effects made predictable: size, boundaries, vocabulary, fusion |
| [Lab 13 — Ordering and Compression Under Budget](lab-13-ordering-and-compression/) | ~50 min | 13, 14 | Mechanical position loss; compression beating truncation on the same budget |

## Chapter-embedded labs

Later chapters carry their lab work directly in the Exercises sections, usually with the assistant's CLI as the instrument:

- Chapter 9's exercises: current-version chunk loading, freshness postures, tenant isolation predicate.
- Chapter 11's worked example + exercises: selection calibration against `rank()`.
- Chapter 18's three-session conflict theater (memory store).
- Chapter 21's research workflow: plan → retrieve → select → draft with interrupt/drift/resume drills.
- Chapter 24's security lab: `projects/advanced/security-test-lab/` — the adversarial environment.
- Chapter 27–28's evaluation work: `projects/advanced/context-evaluation-harness/`.

## How labs are graded (by you, for you)

Each lab's README defines **success** concretely. The honest self-check is the deliverable: if your results table has a real prediction, a real observation, and a real explanation per row — and at least one prediction that was wrong — the lab did its job. Labs with all-correct predictions were scoped too safely; the advanced exercise is standing there for exactly that reason.

## Writing your own lab (the meta-exercise)

Pick a chapter, isolate one mechanism, design the smallest experiment whose outcome would surprise your past self, write the prediction-first protocol, and add it under `labs/` with a README in this house format (Objective → Experiments → Deliverables → Definition of success). A good lab is a gift to the next learner; the pull request is welcome (`CONTRIBUTING.md`).

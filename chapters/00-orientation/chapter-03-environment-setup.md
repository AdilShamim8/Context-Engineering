# Chapter 0.3 — Environment Setup and First Experiment

> Part 0 · Orientation
> Prerequisites: Chapters 0.1, 0.2 · Status: complete
> Time: ~45 minutes

## Overview

In this chapter you make the curriculum's core thesis *observable*: changing the context available to a responder changes the answer — deterministically. You will set up the environment, run the test suite, run the first experiment, and learn to distinguish a deterministic demonstration from model-dependent behavior. This distinction matters everywhere: everything in this repository that claims reproducibility is deterministic, and everything that involves a real model is explicitly labeled otherwise.

## Environment setup

The full walk-through (including troubleshooting) is `docs/getting-started.md`. The short version:

```bash
git clone https://github.com/AdilShamim8/Context-Engineering.git
cd Context-Engineering
python -m unittest discover
```

Requirements: Python 3.10+, nothing else. If the suite reports `OK`, your environment is proven working. **Do not skip the test run** — it is both your setup check and your first example of the evaluation mindset: claims about behavior are checked, not trusted.

## The first experiment

Run:

```bash
python labs/lab-00-first-context-experiment/experiment.py
```

You will see one fixed question — *"How many remote days per week are allowed?"* — answered three times:

```text
=== Scenario 1: empty context ===
Answer: INSUFFICIENT CONTEXT — no evidence available to answer.
=== Scenario 2: current policy (v2, 2026) in context ===
Answer: Employees may work remotely up to 2 days per week.
Citation: hr-remote-work v2 (effective 2026-08-14)
=== Scenario 3: only the stale policy (v1, 2024) in context ===
Answer: Employees may work remotely up to 3 days per week.
Citation: hr-remote-work v1 (effective 2024-02-01)
```

Read the output slowly. Every scenario is the same code, the same question, the same "model." Only the **available context** changed:

1. **No evidence** → an honest refusal. This is *correct* behavior — the responder is built to refuse rather than guess.
2. **Fresh evidence** → a correct answer with a citation.
3. **Stale evidence only** → a confident, citable, **wrong** answer.

Scenario 3 is the heart of context engineering. Nothing crashed. Nothing *looks* wrong. The citation even lends the answer credibility. A user would happily act on outdated information. The failure is entirely in what information was supplied — which means the fix is an engineering fix (versioning, freshness checks, provenance — Part II), not a prompt fix.

## How the responder works (walkthrough)

Open `labs/lab-00-first-context-experiment/experiment.py`. It is deliberately small — around a hundred lines, no imports beyond the standard library. The pieces:

1. **A fixed question.** Not user input; we want reproducibility.
2. **Evidence stores.** Two policy documents, one per scenario, each a dict with text, version, and effective date. This is provenance from day one — the citation in scenario 2 comes from this metadata, not from the text.
3. **A sentence splitter.** A one-line regex (`(?<=[.!?])\s+`) — deliberately naive, and adequate here.
4. **A scorer.** Overlap between the question's meaningful words and each sentence's words. The best-scoring sentence above a threshold becomes the answer; below the threshold, the responder refuses.
5. **A citation.** Whatever won, its document's version and date are attached to the answer.

This is a **rule-based responder**, not a language model. That is the point: it isolates the variable this curriculum teaches. A real model adds fluent language and world knowledge — *and* hallucination risk, cost, and nondeterminism, all of which would contaminate the observation. When the curriculum later needs model behavior (position effects in Chapter 13, response quality in Part VII), it says so explicitly and provides optional model-dependent protocols.

## Deterministic vs. model-dependent: the rule used throughout this repository

| Demonstration | Type | Found in |
|---|---|---|
| What fits in a budget; what gets dropped | Deterministic | Chapters 7, 12, 14 |
| Whether evidence is present, stale, or contradictory | Deterministic | This chapter; Part II |
| Access control keeping restricted docs out of context | Deterministic | Chapters 9, 25 |
| Whether an injection payload is wrapped and screened | Deterministic | Chapter 24 |
| Position effects (does placement change attention?) | Model-dependent (optional protocol) | Chapter 13 |
| Final answer quality | Model-dependent (optional) | Part VII |

If a claim in this repository is about *mechanics* (what fits, what got included, what got cited), it is deterministic and testable — and tested. If it is about *model behavior*, it is either backed by cited research or presented as an experiment protocol for you to run.

## Exercises

1. **Beginner** — Add a third, *contradictory* document to scenario 2 so fresh and stale policies are both present. What does the responder do? (Predict first, then run.) Note: unresolvable contradictions are a context-quality failure; Chapter 4 has the taxonomy.
2. **Intermediate** — Modify the scorer so it down-weights sentences containing the word "was" (a crude past-tense detector). Does scenario 3's behavior change? What does that tell you about scorers vs. policies?
3. **Advanced** — Write a fourth scenario where the *question itself* is unanswerable from any policy ("How many remote days are allowed *for contractors*?"). Confirm the responder refuses. Then make it wrongly answer by lowering the threshold — and explain why thresholds are a policy decision, not a tuning knob to eliminate refusals.

## Common failures

- **"Nothing changed when I edited the documents."** You edited the corpus but the script built its evidence stores from inline literals. Read the code path before assuming magic.
- **"The refusal is annoying — can't it always answer?"** It could; that's scenario 3 with extra steps. Refusal on insufficient evidence is a *feature* you will deliberately engineer in Part IX.
- **"The scorer feels fragile."** Correct — it is ~10 lines. Fragility under realistic queries is exactly why Part II builds real retrieval (BM25, filtering) and Part VII measures it.

## Mastery checklist

- [ ] My test suite passes.
- [ ] I ran the first experiment and can explain scenario 3 as a context failure, not a model failure.
- [ ] I can say what a deterministic demonstration is, and why this curriculum defaults to them.

## Next

Part I begins with Chapter 1 — the discipline defined, its boundaries, and the lifecycle you will implement across the rest of the curriculum.

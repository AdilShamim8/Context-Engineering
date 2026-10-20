# Lab 07 — Chunking and Retrieval Experiments

> Time: ~45 minutes · Deterministic · Chapter tie-ins: 7, 8
> Success criterion: you can predict, then verify, how each chunking change moves retrieval results

## Objective

Develop the calibrated intuition this discipline runs on: *changes to chunking and retrieval parameters produce predictable, measurable effects* — not vibes. You will make three parameter changes and one strategy change, predicting outcomes before running anything.

## Setup

```python
from context_engineering.corpus import load_chunks
from context_engineering.retrieval import LexicalIndex

chunks = load_chunks("datasets/synthetic/corpus")
index = LexicalIndex(chunks)
```

## Experiments

**Experiment 1 — size.** Re-load chunks with `max_words=60`, then `max_words=400`. For each, retrieve with: "How many remote days per week are allowed?" and "What is the vacation carryover rule?" Record top-3 chunk ids and whether the answer sentence is inside one chunk or split across two.

**Experiment 2 — the boundary failure.** Find (or construct) a question whose answer lies at a chunk seam in the `max_words=60` configuration. Then run the same question against the structure-aware default. Write one sentence: what overlap/structure actually bought you here.

**Experiment 3 — vocabulary mismatch.** Query "what is the PTO carryover rule" against the default index. Observe the miss ("PTO" is not in the corpus). Then apply the cheapest Chapter 8 fix (alias table: `{"pto": "vacation"}` — implement `rewrite_query`) and re-run. Record before/after top-3.

**Experiment 4 — fusion.** Build a second "retriever" as a keyword filter over chunk metadata (e.g., boosts chunks whose `heading` contains a query term). Fuse it with BM25 via `rrf_fuse`. Find one query where fusion changes the winner, and explain *why* in terms of ranks, not scores.

## Deliverables

A results table: experiment, prediction, observation, explanation (4 rows). Prediction written *before* running is the whole point — miscalibrated predictions are the best learning signal this lab can produce.

## Definition of success

Each row has a real prediction and a real explanation. At least one prediction should have been wrong; if all four were right, you were too conservative — pick a fifth experiment (reranking with your metadata scorer) until one surprises you.

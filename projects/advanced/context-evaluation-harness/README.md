# Project — Context Evaluation Harness (Advanced)

> Tier: Advanced · Prerequisites: Part VII (Chapters 27–28)
> Implementation: `src/context_engineering/evaluation.py` · Suite: `datasets/synthetic/golden/golden_cases.json` · Runner: `tests/evaluation/test_golden_suite.py`

## Objective

Own the evidence machine: extend the golden suite into a full evaluation harness for *variant comparison* — multiple context strategies measured on the same documented dataset, with case-level reports, ablations, and a written analysis of what the evidence actually supports.

## Requirements

1. **Your own pipeline variants** (at least three): e.g., baseline (as shipped), diversity-off, compression-before-budget, no-current-version-filter, reranked-by-metadata. Each runs the same cases.
2. **Case-level reports**: for each variant × case, the result with named failures — aggregate rates alone are explicitly not acceptable deliverables (Ch. 28).
3. **One ablation with a hypothesis**: written *before* running; then confirmed or refuted, honestly.
4. **Staleness audit**: bump a corpus version in a scratch copy; run; report which cases pin stale facts; update them in one reviewable change set.

## Deliverables

- The harness runner (reusing `run_suite`/`ablate`; extension, not fork).
- The variant × case matrix with annotated deltas.
- The hypothesis and its verdict, with the evidence table that settled it.
- The staleness-audit diff (corpus edit + case updates, one commit).

## Evaluation criteria

| Criterion | Pass standard |
|---|---|
| Comparability | Identical cases across variants; one variable per variant |
| Attribution | Every delta traced to a mechanism, not a narrative |
| Honesty | Refuted hypotheses stated as refuted; noise named as noise |
| Hygiene | Cases written from corpus/policy, never from system outputs |

## Definition of success

Someone reading only your matrix and hypothesis-verdict can decide which variant should ship — and can point to the specific cases that would make them wrong.

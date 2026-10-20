# Project — Retrieval and Context Assembly Engine (Intermediate)

> Tier: Intermediate · Prerequisites: Parts II–III (Chapters 7–14)
> Implementation: `src/context_engineering/{retrieval,provenance,selection,budget,assembly,compression}.py`

## Objective

Build the full candidate-to-request engine on the Nimbus corpus: retrieve under access policy → select with composite ranking → budget under pressure → assemble labeled and ordered — then *compare variants* on a small hand-built question set rather than shipping the first configuration that works.

## Requirements

1. **A one-call API.** `build_request(question, access_levels, budget, config) -> (AssembledContext, AllocationResult, trace_list)` composing all Part II–III stages.
2. **Configurable variants.** At minimum: ordering strategy, selection policy knobs (`max_items`, diversity on/off), and compression-before-budget on/off.
3. **Version-aware retrieval.** Only current document versions may become candidates (Chapter 9).
4. **Audit trail.** The allocation report and a per-stage trace ship with every request.

## Deliverables

- The engine (library extensions; keep it composable, no god-functions).
- A comparison table over ≥8 questions × ≥3 variants (baseline / diversity-off / compression-on): which questions changed, which answers degraded or improved, with assembled contexts saved for the deltas.
- A one-page analysis: which variant ships as default, justified by the table, with the two failure cases each losing variant would introduce.

## Evaluation criteria

| Criterion | Pass standard |
|---|---|
| Correctness | Restricted/superseded content unreachable in every variant (tests) |
| Comparability | All variants run identical questions; one variable at a time |
| Honesty | At least one case where the "obvious" variant loses, analyzed |
| Audit | Every request reproducible from question + config |

## Definition of success

A teammate can change one config flag, re-run, and see *which* questions changed and *why* — without reading your code.

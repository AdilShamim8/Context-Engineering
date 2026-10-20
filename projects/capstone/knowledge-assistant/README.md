# Project — Context-Aware Knowledge Assistant (Capstone)

> Tier: Capstone · Prerequisites: Parts I–VII (Chapter 34–35)
> Implementation: `src/context_engineering/apps/knowledge_assistant.py` + CLI `ask` / `evaluate`
> Tests: `tests/integration/test_knowledge_assistant.py`, `tests/evaluation/test_golden_suite.py`

## Objective

Move from "the curriculum's assistant works" to "I own an assistant I can defend": extend it, break it on purpose, fix it with evidence, and produce the evidence pack that proves each behavior.

## The system as shipped

```bash
# The question you know
PYTHONPATH=src python -m context_engineering.cli ask "How many remote days per week are allowed?"

# Same question, restricted caller → honest refusal
PYTHONPATH=src python -m context_engineering.cli ask "What are the salary bands for engineering level 3?"

# Authorized caller → correct answer with restricted-document citation
PYTHONPATH=src python -m context_engineering.cli ask "Which service had the path validation vulnerability?" \
    --access restricted:security-team

# The exact assembled request + the stage trace
... --show-context --show-trace

# Blocking screening policy: high-severity content dropped, trace shows it
... --screening block

# The acceptance criteria, on demand
PYTHONPATH=src python -m context_engineering.cli evaluate
```

## Ownership pass (the project work)

1. **Extend the domain.** Add ≥2 new synthetic documents (new policy areas; one with a restricted class) with full manifest governance, and ≥3 new golden cases including one authorization-pair (refuse-for-general / answer-for-authorized).
2. **Break three things on purpose**, one per layer: (a) remove current-version filtering — watch gc-01 fail on the stale number; (b) run access filtering *after* ranking — construct the query that leaks shape (Ch. 9's k-truncation argument, made real); (c) halve the budget — watch truncation eat a required fact. For each: prediction first, trace + suite output second, fix third.
3. **One ablation**: diversity off, hypothesis written first, case-level deltas analyzed (Ch. 38's posture at small scale).
4. **The evidence pack**: suite report before/after each break; the three failure traces annotated; the ablation verdict; and the architecture brief (what you would keep/replace/extend in production, per component, with reasons).

## Evaluation criteria

| Criterion | Pass standard |
|---|---|
| Governance | New docs fully manifested; loader strictness intact |
| Honesty | Refusal-pair cases present and passing for your content |
| Evidence | Every break/fix documented with trace + suite output |
| Defense | A reviewer's "show me" on any behavior resolves to an artifact |

## Definition of success

`evaluate` is green with your cases included, and your evidence pack lets a stranger reconstruct every decision — the pack is the deliverable; the assistant is its exhibit.

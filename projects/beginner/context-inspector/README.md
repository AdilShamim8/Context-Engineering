# Project — Context Inspector (Beginner)

> Tier: Beginner · Prerequisites: Parts I–III (Chapters 3, 13, 24)
> Implementation: `src/context_engineering/{context,assembly}.py` + CLI `inspect` · Tests: `tests/unit/test_assembly.py`, `test_cli.py`

## Objective

Build the single highest-leverage tool in this repository: one that makes the assembled request *visible*. Most production LLM failures are debugged by people arguing about what the model probably saw; the inspector ends the argument — the request is a rendered artifact you can read, with every component labeled, delimited, and traceable.

## The tool, as shipped

```bash
# component overview + the full assembled request text
PYTHONPATH=src python -m context_engineering.cli inspect

# annotate component boundaries in the assembled text
PYTHONPATH=src python -m context_engineering.cli inspect --mark-spans
```

## What to look for (guided inspection)

Run the inspector on the demo bundle and answer from *the rendered text*, not from memory of the JSON:

1. **Trust boundaries.** Find the `<<<UNTRUSTED ... >>>` regions. Which components are inside them, and why is each one there? (Chapters 3, 24: evidence and tool results are data; instructions are policy.)
2. **Provenance visibility.** Pick the `ev-remote-v2` block. What can a reader learn about this evidence *without leaving the rendered request*? (id, version, effective date — the citation is pre-assembled.)
3. **Ordering consequences.** In the kind-grouped output, where did the stale v1 policy land relative to v2? Where would a budget cut take content first? Cross-check against the `budget` command's report at `--total 1150`.
4. **The instruction/nearest-evidence gap.** Measure (in rendered lines) how far the instruction block sits from the best evidence. Then write one sentence: in what failure would this distance matter? (Chapter 13's position effects — the inspector is how you'd notice.)

## Your work on this project

1. **The four guided answers** above, each citing the rendered text.
2. **Build a diff-inspector** (the real deliverable): a small script that takes two bundle files (or two orderings) and prints *only the differences* between their assembled requests — added/removed/relabeled components and changed spans. Debugging is comparison; make the tool do it.
3. **Inspect your own bundle** (stretch): write a bundle JSON representing a real assistant request you know (anonymized, synthetic content only) and inspect it. Most people find something they did not expect — usually untrusted content rendered with no provenance.

## Deliverables

- The four guided answers.
- The diff-inspector script (in your fork or a lab directory) with two example outputs.
- (Stretch) your own bundle + one-paragraph surprise report.

## Evaluation criteria

| Criterion | Pass standard |
|---|---|
| Visibility | All trust labels, provenance headers, and delimiters named correctly |
| Comparison | Diff-inspector correctly isolates changes between two variants |
| Honesty | Surprise report documents a real observation, or states there was none and why |

## Definition of success

From now on, when an LLM application misbehaves, your first reflex is "dump the request" — and you have the tool to do it in one command.

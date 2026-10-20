# Chapter 13 — Context Ordering and Position Effects

> Part III · Dynamic Context Construction
> Prerequisites: Chapter 10 · Status: complete
> Time: ~60 minutes

## Overview

Order is the most under-engineered decision in context construction: most systems order by accident of insertion. But research and practice agree that **where** information sits can change whether it is used. This chapter covers the evidence (especially *Lost in the Middle*), the ordering strategies implemented in `assembly.py`, the honest limits of what a deterministic pipeline can demonstrate about position, and a protocol for measuring positional effects on your own model and task rather than trusting folklore.

## The evidence: position matters

Liu et al. (2023) — *Lost in the Middle: How Language Models Use Long Contexts* — is the canonical reference. Their experimental setup: place the answer-bearing document at controlled positions within a long context and measure multi-document QA accuracy. The widely-cited result: performance tends to be best when key information appears near the **beginning or end** of the context, often degrading when it sits in the **middle** — a roughly U-shaped positional curve. Findings like this have been replicated across model families with varying strength, and later work continues to document positional sensitivity in long contexts.

Three careful readings, because the citation is often abused:

1. **Effect sizes vary by model and task.** The U-shape is a recurring pattern, not a law; different models, prompt formats, and context lengths show it with different intensities — and newer long-context models are specifically trained against it with results you should verify rather than assume either way.
2. **It does not prove "middle is always bad."** It proves "position is a variable you must treat as a variable." For some tasks the effect is negligible; for retrieval-style QA it is often material.
3. **Your model, your task, your measurement outrank any paper.** That is why this chapter's deliverable is a measurement protocol, not a rule to memorize.

## Ordering strategies, as code

`OrderingStrategy` in `assembly.py` implements four deliberate arrangements:

- **KIND_GROUPED** (the default): instructions first, then state, tool definitions, user input, history, memory, evidence, tool results, derived. The logic is trust- and structure-shaped: the model meets its task before its materials; trusted framing precedes untrusted data (also a security property, Chapter 24).
- **PRIORITY_ORDER / PRIORITY_REVERSED**: by importance ascending or descending — the "important first / important last" pair that long-context heuristics trade against each other (front = strongest serial position; end = strongest recency).
- **STABLE**: as given — useful as a control condition for experiments, and the default of careless systems.

The non-obvious point: **assembly order is testable architecture.** The unit tests pin KIND_GROUPED placing instructions first regardless of input order; your production system deserves the same pin.

## Position effects you can demonstrate deterministically — and the ones you can't

A rule-based responder has no attention mechanism, so *model* position effects are outside what our deterministic stack can show. What the deterministic stack *does* show is the mechanical precursor: **budget-driven positional loss.** With important-last ordering and a tight budget, the allocator truncates from the *bottom*; with important-first, from the top — the Lab 13 experiment makes this visible: the same components, same budget, and the answer survives under one ordering and is cut in half under the other. Mechanical position loss is real, deterministic, and testable; model position effects are real, model-dependent, and measurable only with a model. Confusing the two is how folklore starts, and this curriculum keeps them explicitly separate.

## The measurement protocol (model-dependent, optional)

For teams with API access, the protocol for measuring positional effects on *your* system — run it before committing to an ordering strategy:

1. **Build a fixed test set**: 20–50 questions with known answer locations in the corpus.
2. **Control everything except position**: same retrieval, same budget, same prompt template; only the evidence order varies.
3. **Sweep positions**: place the answer-bearing chunk at position 1, middle, last of the evidence block (and, if your contexts are long, at 10%/50%/90% of total context).
4. **Run ≥3 repeats per position** (nondeterminism matters; report means and spread).
5. **Score answers** with the Chapter 27 harness (fact coverage, citation correctness), not vibes.
6. **Decide**: if the curve is flat on your model/task, stop optimizing order and spend effort on selection; if it is U-shaped, put critical evidence at your measured-best position and encode it in `OrderingStrategy` as a tested default.

Cost note: this protocol consumes API budget proportional to questions × positions × repeats. Start with the smallest version that would change your decision.

## Worked example: the same question, three orders, one budget

Take the carryover question with 5 evidence chunks (the answer in chunk 3), instructions, and a budget tight enough to truncate the last component. Run all four strategies and diff the assembled texts: under KIND_GROUPED the evidence order follows selection rank; under PRIORITY_REVERSED the *lowest*-priority chunk now sits at the truncation boundary. The assembler's `spans` map tells you exactly where every component landed — so "did the answer-bearing chunk survive *intact*?" is a lookup, not a reading exercise. That lookup is what your production traces should perform per request (Chapter 29).

## Exercises

1. **Beginner** — Assemble the worked example and use `AssembledContext.component_text()` to prove where the answer chunk landed under each of the four strategies. Write one sentence per strategy about what a budget cut would take.
2. **Intermediate** — Implement `IMPORTANT_MIDDLE` as a new strategy (highest-priority content dead center). Construct the argument for when such placement could be right (hint: filler-protected contexts); then run Lab 13 and let the mechanical results argue back.
3. **Advanced** — Run the measurement protocol's smallest version against a real model with 5 questions × 3 positions × 3 repeats. Report the curve and your resulting ordering decision. If you have no API access, write the protocol as a runnable experiment module behind the optional adapter boundary, with the dataset and scorer fully built.

## Common failures

- **Insertion-order assembly.** Whatever the code appended last sits last; nobody can explain why the answer improved when a refactor shuffled the list.
- **Folklaw overfitting.** "Put everything important at the end" applied to a task where the measured curve was flat — wasted effort that displaced real selection work.
- **Ignoring mechanical position loss.** Studying model attention while the allocator quietly truncates the bottom of the context every request. Check the mechanical layer first — it is deterministic and free to inspect.

## Summary

- Position is a real variable: U-shaped effects are documented (Liu et al. 2023), vary by model/task, and are measurable with a controlled protocol.
- Four strategies make order a tested architectural decision; mechanical position loss (budget × order) is deterministic and visible in `spans`.
- Measure on your own model before believing any ordering rule; the protocol is the deliverable.

## Mastery checklist

- [ ] I can state the Lost in the Middle finding and its honest caveats.
- [ ] I can demonstrate mechanical position loss with the assembler and explain why it is not a "model effect."
- [ ] I can run (or spec) the position-sweep protocol and turn results into a tested default.

## Review questions

1. Why is STABLE ordering valuable despite being "no strategy"?
2. What can a deterministic pipeline prove about position, and what requires a model? Why does the curriculum refuse to blur this?
3. Why does the measurement protocol freeze everything except position?

## References

- Liu et al., *Lost in the Middle* — https://arxiv.org/abs/2307.03172 (reviewed 2026-10-20)
- Implementation: `src/context_engineering/assembly.py`; tests `tests/unit/test_assembly.py`.

## Next

Chapter 14: compression — shrinking content *before* the budget has to truncate it.

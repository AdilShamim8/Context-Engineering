# Chapter 35 — Context-Aware Knowledge Assistant

> Part IX · Integration and Capstone
> Prerequisites: Chapter 34 · Status: complete
> Time: ~90 minutes (plus project time)

## Overview

The flagship: a question-answering assistant over the Nimbus corpus that retrieves evidence, filters by access, screens untrusted content, selects within a budget, assembles with labels, answers with citations — and *refuses honestly* when evidence is missing or unauthorized. You have already run it (`python -m context_engineering.cli ask ...`); this chapter is the build-and-own pass: how each stage earns its place, what the golden suite demands of it, and what changes when a real model joins.

## The request path, annotated by chapter

```python
# apps/knowledge_assistant.py — read alongside this table
hits = index.search(question, k=8, predicate=policy.as_predicate())
#   Ch. 7: BM25 over current-version chunks | Ch. 9: access BEFORE ranking
#   Ch. 5: index built from current versions only (supersession is structural)
findings → screened = [h for h in hits if not blocked]      # Ch. 24: detect + policy
selected = rank(hits)                                        # Ch. 11: composite + dedup + diversity
allocation = allocate([instruction] + components, budget)   # Ch. 12: reasons recorded
assembled = assemble(allocation.selected)                    # Ch. 13 order; Ch. 24 delimiters
answer = DeterministicResponder().answer(question, bundle)   # Ch. 0.3: refusal is a feature
```

Every stage's contract is pinned twice: once by its unit tests, once end-to-end by the golden suite running *through the app* (`TestCapstoneAgainstGoldenSuite`). The 12 cases are the assistant's acceptance criteria: version conflict resolved (v2 wins), restricted questions refused for general users *and answered for authorized ones*, no-evidence refusal, injection fixture labeled and contained, numbers intact.

## The three behaviors that make this more than a demo

1. **Honest refusal.** Ask about compensation as a general employee: `insufficient_evidence`, citations empty. The system's integrity is defined by what it refuses to answer without authorization — Chapter 9's filter means the model *cannot* have leaked content in context, so the refusal is structural, not polite.
2. **Version-aware citation.** "hr-remote-work v2 (2026-08-14)" — the citation carries what the reader needs to verify: which document, which version, when effective. v1 is *unreachable*: `current_chunks` filtered it before any scoring, so no ranking luck can ever serve it.
3. **Inspectable everything.** `--show-context` prints the exact assembled request (the Chapter 1 habit); `--show-trace` prints the stage trace with hits, drops, findings, tokens. Debugging the assistant means reading its own account of itself.

## Handling insufficient evidence — the design commitment

Three ways systems fail at "we don't know": answer anyway (hallucination), refuse everything (useless), or refuse precisely (the goal). The assistant's mechanisms, inherited from earlier chapters: coverage threshold at the responder (Ch. 0.3), `min_score` at selection (Ch. 11), and access filtering that makes unauthorized content *invisible rather than forbidden* (Ch. 9 — a crucial distinction: the model never sees restricted text, so it cannot be talked out of ignoring it). The golden suite's refusal cases (gc-07, gc-08, gc-10) pin the third way, and its authorization case (gc-09) pins the flip side: the same question, asked by an authorized caller, must be *answered* — refusal systems that over-refuse are as broken as ones that over-answer.

## Wiring a real model (what actually changes)

The model boundary is the responder: everything upstream (retrieve → screen → select → budget → assemble) is model-independent and stays untouched. A real model changes four things, each with its protocol: (1) answers become paraphrased, so golden cases check grounding (facts/citations/refusals), never exact strings (Ch. 27); (2) positional behavior becomes real, so run the Ch. 13 protocol per model; (3) token costs become exact rather than estimated, so re-calibrate budgets (Ch. 2/31); (4) instruction-following becomes a live input, so the INSTRUCTION_TEXT gets prompt-engineered — *finally* legitimately — while the trust architecture (wrapping, screening, access) stays exactly as built, because that is the entire lesson of Chapter 24.

## Project: own it

The project spec (`projects/capstone/knowledge-assistant/README.md`) drives the ownership pass: run the suite, extend the corpus, break three things on purpose, add your own golden cases, and defend your changes with evidence. The capstone's real deliverable is the *evidence pack*: suite report before/after each change, the traces that explain each failure, and the written decisions — the portfolio artifact that says "context engineer," not "tutorial completer."

## Exercises

1. **Beginner** — Run all five CLI variants in the spec (default, restricted-user, authorized-user, block-screening, tight-budget) and annotate the one line of output that differs in each, naming its chapter.
2. **Intermediate** — Extend the corpus with a genuinely new document (your own fictional policy), add two golden cases for it, and make the suite pass — including one access-class case if your document warrants it.
3. **Advanced** — Implement the model-backed responder behind the boundary (optional API adapter), run the Ch. 28 model-protocol (n≥3, grounding checks, variance report), and write the before/after analysis: which golden behaviors held, which degraded, and what you would tune first.

## Mastery checklist

- [ ] I can trace any assistant behavior to its owning stage and chapter, from the trace alone.
- [ ] I can add corpus content + golden cases and get the suite green in one coherent change.
- [ ] I can articulate exactly what changes (and what must not) when a real model is wired in.

## Next

Chapter 36: giving the assistant memory and session state — the stateful upgrade.

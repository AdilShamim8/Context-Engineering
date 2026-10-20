# Chapter 14 — Context Compression and Summarization

> Part III · Dynamic Context Construction
> Prerequisites: Chapter 12 · Status: complete
> Time: ~60 minutes

## Overview

Compression answers the budget problem one stage earlier than truncation: instead of allocating full components and cutting what doesn't fit, shrink components *deliberately* — keeping what the task needs, discarding what it doesn't. But compression is a destructive operation: every compression step risks losing exactly the detail that mattered. This chapter teaches the compression ladder from cheapest to riskiest, the must-preserve principle implemented in `compression.py`, and how to *measure* compression loss instead of hoping it away.

## The compression ladder

Ordered by safety — always exhaust a lower rung before climbing:

| Rung | Technique | Loses | Cost | In library |
|---|---|---|---|---|
| 1 | **Deduplication** | Nothing (true redundancy) | ~Free | `deduplicate` |
| 2 | **Structural pruning** | Boilerplate, headers, nav residue | Layout context | (ingestion, Ch. 6) |
| 3 | **Selective deletion** | Whole low-value components | What the "low-value" call missed | selection (Ch. 11) |
| 4 | **Extractive compression** | Non-selected sentences | Nuance, connective reasoning | `extractive_compress` |
| 5 | **Structured notes / rolling summaries** | Detail → schema-shaped facts | Everything off-schema | `structured_notes` |
| 6 | **Abstractive summarization** | Everything the model decides to | Whatever the model gets wrong or invents | behind adapters (optional) |

The unit of loss grows with each rung. Rung 1 is free insurance; rung 6 is a model call with hallucination risk and nondeterminism. The industry's habitual error is jumping to rung 5–6 for problems rungs 1–4 solve — "summarize the history" before "delete the duplicate turns."

## What must survive: the pinned-fact principle

`extractive_compress` encodes the chapter's central rule: **compression must preserve what the task cannot afford to lose before it optimizes for anything else.** Pinned patterns — numbers, dates, identifiers, and constraint words (*must, never, only, required, forbidden*) — are included first, even when they sit in "boring" sentences. The unit tests demonstrate the extreme case: aggressive compression that still retains "the stipend is 300 dollars per quarter" and drops warm filler. Also deliberate: the compressor **preserves original sentence order** — reordering procedural or causal text changes meaning even when every sentence survives.

The general form, beyond this implementation: every task has a *loss budget* — classes of fact whose loss converts a correct answer into a confident wrong one. Money, dates, quantities, exceptions, identities, and negations are almost always in it. Prose warmth, repeated framing, and tangents almost never are. **Name your task's loss budget explicitly, in code or in review checklists**, because "the summary looked fine" is not evidence — Chapter 27's coverage metrics on required facts are.

## Structured notes and rolling summaries

Rung 5 replaces free text with a fixed schema: `- User prefers morning meetings`, `- Ticket escalated 2026-10-12`, `- Constraint: no PII in logs`. Why schema: notes are inspectable (a bullet is a claim), bounded (each note costs a known handful of tokens), and loss becomes *visible* (what fell off the schema is a smaller, more predictable surface than what fell off a paragraph). `structured_notes` implements this deterministically; Chapter 17 uses it for rolling history summaries, Chapter 21 for agent scratch notes. The named risk: **schema myopia** — anything that doesn't fit the schema silently disappears. The mitigation is a deliberately designed schema *per task* (what kinds of fact will later matter?) plus spot-check audits against the original source (Chapter 28).

## Abstractive summarization: the rung that needs a model

Model-written summaries are fluent, context-aware, and lossy in the most dangerous way: loss *reads* like success (a fluent summary of the wrong facts). If you use rung 6: summarize with the task stated (not "summarize this" but "list the constraints affecting X"), keep provenance attached to summaries (a DERIVED component carrying the source chain), preserve pinned facts verbatim rather than trusting paraphrase, and — above all — measure: coverage of required facts (summarized vs. original), before/after on the eval suite, and spot audits. Anthropic's agent guidance frames this as compaction and structured note-taking as core agent operations (reviewed 2026-10-20) — the industry has learned that *structured, verifiable* compression beats free-form summarization for reliability.

## Worked example: compressing tool output under budget

A calendar tool returned 900 tokens; the budget (Chapter 12's report) truncated it to 47 head tokens, cutting the meeting time — the one fact the user asked about. The compression-first alternative: run `extractive_compress(payload, max_tokens=120)` *before* allocation: pinned sentences (dates, times, attendee lists) survive; chatty availability narrative goes; the allocator now fits 120 real tokens instead of 47 accidental ones. Same budget, more signal — that is the entire argument for compression-before-allocation, and Lab 14 has you reproduce both paths and diff the assembled contexts.

## Exercises

1. **Beginner** — Take the support-playbook's customer-facing sections and compress to 30 tokens with the default pinner; then list what a *ticket-handling task* lost that a *morale-summary task* didn't. Same input, different loss budget — write both down.
2. **Intermediate** — Extend `MUST_PRESERVE_PATTERNS` with negation pinning (`not`, `no more than`, `cannot`) and write the failing-test-first demonstration: a policy sentence whose meaning inverts without the negation. (This is the highest-leverage pattern class most real systems forget.)
3. **Advanced** — Build the compression loss audit: given original and compressed texts plus a required-fact list, report kept/lost/invented facts (invented detection: numbers in the summary absent from the source). Run it on your Lab 14 outputs. An ablation-grade deliverable: original vs. compressed context on the golden questions — where did compression change answers, and was the change loss, gain (noise removed!), or neutral?

## Common failures

- **Summarize-first reflex.** Jumping to rung 6 when dedup (rung 1) was the actual problem. Diagnose redundancy before paying for models.
- **The fluent-loss trap.** Trusting summaries because they read well; coverage metrics exist because eyeballs are not measurement.
- **Losing negations.** "You may work remotely 3 days" summarizing "may not exceed 3 days" — negation loss inverts policy. Pin or measure.
- **Compression without provenance.** Summaries entered as context with no source chain; Chapter 26's audit trail becomes impossible for exactly the content most likely to have been distorted.

## Summary

- Climb the ladder: dedup → prune → delete → extract → notes → abstractive; each rung's loss profile is known.
- Pinned facts (numbers, dates, IDs, constraints, negations) outrank style; order is meaning; schemas make loss visible.
- Model-written summaries need the same evidence discipline as any model output: task framing, provenance, coverage measurement.

## Mastery checklist

- [ ] I can name the ladder's rungs, what each loses, and which library function implements it.
- [ ] I can define a task's loss budget and extend the pinning patterns with a test-first example.
- [ ] I can demonstrate compression-before-allocation beating truncation on the same budget.

## Review questions

1. Why is deduplication "free insurance" while abstractive summarization is the riskiest rung?
2. Why does `extractive_compress` keep original order, and what task classes would violate that?
3. What would a coverage metric for compression check, and against what source?

## References

- Anthropic, *Effective context engineering for AI agents* — compaction and structured note-taking in agent loops — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (reviewed 2026-10-20)
- Implementation: `src/context_engineering/compression.py`; tests `tests/unit/test_compression.py`.

## Next

Chapter 15: progressive disclosure — the radical compression of not including things yet.

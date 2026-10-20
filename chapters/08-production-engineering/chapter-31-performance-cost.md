# Chapter 31 — Performance, Cost, and Scalability

> Part VIII · Reliability, Performance, and Production
> Prerequisites: Chapter 30 · Status: complete
> Time: ~55 minutes

## Overview

Context systems have a cost curve, and it is usually steeper than anyone budgeted: every token is paid (and re-paid per turn), every retrieval stage adds latency, every model call adds seconds, and "just add more context" scales the bill linearly with the least useful content. This chapter turns Chapter 12's budgeting and Chapter 29's metrics into an economics discipline: what to measure, what the levers are, and — the core skill — **trade-off analysis that compares strategies on the criteria that matter instead of optimizing one number in isolation.**

## The cost model of a context system

Four cost centers, in the order teams usually discover them:

1. **Token cost.** Input tokens are billed per request — and in multi-turn systems, *re-billed every turn* (Ch. 2's whole-window-processing). A 6K-token context over a 10-turn session is 60K billed input tokens, most of it identical. This is why Chapter 16's caching and Chapter 14's compression are cost features, not just quality features.
2. **Latency.** Retrieval (fast), reranking (model-priced), progressive disclosure (round-trips), generation (the long pole). Per-stage timings from Chapter 29's traces turn "the system feels slow" into a named stage with a p95.
3. **Compute around the model.** Embedding, indexing, screening, compression — the deterministic stages are cheap per request and easy to forget until the corpus grows (re-embedding an entire corpus on a version bump is a real cost event; Ch. 16's invalidation rules decide how often it fires).
4. **Human cost.** The most expensive line item: labeling eval sets, reviewing conflicts, maintaining golden cases. Budget it deliberately (it is what keeps every other line honest) or pay it incidentally (in outages).

The measurements that make these visible are already in the stack: allocation reports give per-request and per-kind token totals; traces give per-stage latency; the eval harness runs A/B on cost *as a first-class metric* — every comparison in Chapter 28's ablation discipline reports tokens and latency alongside correctness, because **a strategy that improves quality at 3× cost is a different strategy, not a better one.**

## The levers, and what each trades

| Lever | Saves | Costs | Chapter |
|---|---|---|---|
| Compression before allocation | Tokens per request | A model call or extractive loss risk | 14 |
| History bounding + rolling summaries | Tokens per turn, growing | Commitments carried by schema, not prose | 17 |
| Progressive disclosure | Tokens for unused content | Round-trips, tool-choice risk | 15 |
| Retrieval caching | Latency, repeated compute | Invalidation complexity, staleness risk | 16 |
| Fragment reuse / stable prefixes | Provider-cache hit rate | Assembly-order rigidity | 13, 16 |
| Smaller selection (max_items) | Tokens, noise | Coverage (recall) | 11, 12 |
| Batching & concurrency | Throughput | Burst limits, per-request observability | 30 |
| Smaller/cheaper models per stage | Cost everywhere | Capability cliffs — must be re-evaluated | 28, 33 |

Read the third column as the chapter's thesis: **no lever is free**; each is a trade you measure on your eval suite and price on your ledger. The failure mode is applying levers by fashion (vector DB before semantic need, chatty rerankers before the recall gap is measured) — Chapter 8's four-question justification, now with prices attached.

## Trade-off analysis: the method

When comparing context strategies, hold Chapter 27's discipline and add the economics:

1. **Same cases, one variable, full metrics.** Correctness (golden suite) + latency (per-stage) + tokens (per request) — all three, always. A table without tokens is half a decision.
2. **Price it at your scale.** Per-request numbers mean nothing until multiplied by your traffic and session shape: "saves 1.2K tokens per turn" × 10 turns × daily sessions is the actual number. Do this arithmetic *in the report* — the Chapter 16 advanced exercise's break-even computation is the pattern.
3. **Find the knee.** Most strategies have a sweet spot then diminishing returns: max_items=8→12 might buy +2% coverage for +30% tokens; the knee was at 10. Report the curve, not the endpoint.
4. **Name the failure mode each lever introduces.** Compression can drop pinned facts (test it); progressive disclosure can leave pointers unfollowed (trace it); aggressive caching can serve stale policy (invalidate it). A trade-off analysis that doesn't name what can now break is marketing.

## Worked example: pricing the compression lever honestly

From the Chapter 14 lab data (your numbers will differ; the method transfers): a 590-token policy component, truncated to 132 by the allocator, *cost the answer* — the compressed-at-120 version preserved it. The naive analysis: "compression adds a deterministic step and saves 0 tokens (both fit 120)." The honest analysis: compression *saved the request from needing 590 tokens* — under a tighter budget class (smaller model, cheaper tier), the truncation path fails the golden case and compression passes it. So the lever's value is not "tokens saved at fixed quality" but "quality floor maintained at a cheaper budget class." That reframing — **levers move you between (cost, quality) points, and the eval suite tells you which moves are legal** — is the entire chapter in one sentence.

## Scalability: the shape of growth

Three growth axes, each with a known failure: **corpus growth** (linear scan becomes retrieval infrastructure; re-embedding costs scale with size — Ch. 16's invalidation policy is the mitigation; the honest note: BM25-style lexical search scales remarkably far, which is why the baseline endures); **traffic growth** (per-request costs × N; caching and batching are the levers; observability must stay per-request or regressions hide in averages); **session length growth** (tokens × turns; history management is the entire ballgame — Ch. 17). Design questions belong to the axis: "will this survive 10× documents / 10× traffic / 10× turns?" — three different tests.

## Exercises

1. **Beginner** — Build the cost table for the capstone assistant: tokens per request (allocation report), per-stage latency (trace), at two budget classes (8192/1024 and 4096/512). Report both runs' golden-suite results side by side.
2. **Intermediate** — Run the max_items curve: 4/6/8/10/12 on the golden suite, plotting coverage and tokens per case. Identify your knee and justify your default with the curve, not the midpoint habit.
3. **Advanced** — The break-even memo: pick a lever (caching, compression, progressive disclosure) and compute the scale at which it pays for itself (including the complexity cost, priced at your hourly engineering rate — state your assumption). Hand the memo to someone and have them attack it; revise.

## Common failures

- **Optimizing latency into quality loss.** Cutting retrieval k or context size for speed without re-running the suite; "faster wrong answers" is a real product state.
- **Per-request myopia.** Improvements reported without the ×N arithmetic; the trade looked free at n=1.
- **The cache that pays twice.** Cost "savings" from caching measured without invalidation overhead at the corpus's real change cadence.
- **Human-cost blindness.** Eval maintenance unbudgeted; the suite decays; every other number quietly follows.

## Summary

- Four cost centers: tokens (re-billed per turn), latency, compute, humans — all measurable from existing artifacts.
- Every lever trades something; the eval suite + ledger decide which moves are legal and which are cheap.
- Growth has three axes — corpus, traffic, turns — each with its own failure and its own tests.

## Mastery checklist

- [ ] I can produce the three-metric comparison (correctness, latency, tokens) for two variants from the existing stack alone.
- [ ] I can find and defend a knee on a lever curve.
- [ ] I can write a break-even memo with stated assumptions and survive an attack on it.

## Review questions

1. Why are compression and caching *cost* features, not just quality features — what line item does each attack?
2. What makes "quality floor maintained at a cheaper budget class" a better framing than "tokens saved"?
3. Which growth axis does history management own, and what does its failure curve look like?

## References

- Artifacts used: `budget.py` (token ledgers), `observability.py` (per-stage latency), `evaluation.py` (suite comparisons); OWASP "unbounded consumption" — the failure family bounded-budget design prevents — https://owasp.org/www-project-top-10-for-large-language-model-applications/ (reviewed 2026-10-20)

## Next

Chapter 32: deployment, monitoring, and the maintenance discipline that keeps it all true over time.

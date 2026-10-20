# Chapter 2 — LLM Inputs, Tokens, Inference, and Context Windows

> Part I · Foundations
> Prerequisites: Chapter 1 · Status: complete
> Time: ~75 minutes

## Overview

Context is a physical, countable resource, and this chapter teaches you to count it. You will learn what tokens are, why they are the unit of cost and capacity, how to estimate them without a model provider, how to budget input and output against a fixed window, and — crucially — why a larger context window does not make context engineering obsolete. The chapter's ideas are implemented in `src/context_engineering/tokens.py` and `budget.py`, which you will run in the Chapter 12 lab; here you build the understanding that makes those tools meaningful in your hands.

## What tokenization actually is

Models do not read characters or words. They read **tokens**: sub-word units produced by a tokenizer (typically a byte-pair-encoding variant) before training and inference. Rough rules of thumb for English text on modern tokenizers (verified against provider documentation guidance; reviewed 2026-10-20): a token is around four characters, or about ¾ of a word. But the variance is the lesson, not the average:

- Common words are usually single tokens ("the", "work").
- Rarer or longer words split: a technical identifier like `max_context_budget_tokens` can cost five or more tokens.
- **Whitespace is not free**: leading spaces are often their own tokens — the same sentence re-indented can cost measurably more.
- Non-English text frequently costs more tokens per idea — a fixed window buys fewer words.
- Structured formats (JSON, XML, code) interleave punctuation and whitespace that inflate counts relative to the information they carry.

**Consequences you will use constantly:** (1) "word count" is not capacity; (2) two renderings of the same information can differ meaningfully in cost — this becomes a real lever in Chapter 14 (compression) and 16 (caching); (3) estimates are planning tools, never billing truth — exact counts come from the provider's tokenizer, and provider-dependent limits must be verified against current documentation before you rely on them.

## The context window and its three budgets

The **context window** is the maximum token count the model accepts per request. But thinking of it as one number misleads. Every request actually juggles three interacting budgets:

1. **Input budget** — everything you assemble: instructions, history, evidence, tool definitions, tool results, memory. This is the budget you *engineer*.
2. **Output budget** — the response consumes window capacity too. Most provider APIs let you cap expected output; an unbounded answer can fail or be cut off mid-stream.
3. **Effective working set** — window minus committed-but-unproductive content: framing, delimiters, duplicated boilerplate, stale history. The gap between "window size" and "usable, high-value context" is exactly what this curriculum teaches you to measure and manage.

The practical failure mode of ignoring the output budget is well known to anyone who has hit mid-generation cutoffs: the model runs out of window while answering. The failure mode of ignoring the effective working set is subtler: the request "fits" but important evidence was pushed out by junk that no longer earns its space.

## Estimating without a provider

You should be able to estimate capacity *before* building anything. The library's heuristic (see `tokens.py`) combines the two standard rules — a characters-per-token floor and a words-based estimate, taking the larger — and its docstring is explicit that it is a **planning heuristic, not a bill**. That honesty is deliberate and is the pattern throughout: deterministic tools for deterministic facts; verified provider tokenizers for exact counts; never confuse the two.

Worked example, the shape you will repeat throughout the curriculum:

```text
Instructions template        ~350 tokens
Conversation history (20 turns, unmanaged)  ~2,800 tokens
Retrieved evidence (8 chunks × ~180 tokens) ~1,440 tokens
Tool definitions (4 tools)   ~600 tokens
Pinned memory notes          ~250 tokens
Subtotal input               ~5,440 tokens
Reserved output              1,020 tokens
Total committed              ~6,460 of 8,000-token window
Slack for safety margin      ~1,540 tokens
```

Reading such a ledger, the engineering questions write themselves: Does unmanaged history (2,800) earn 43% of committed capacity? Which eight chunks — chosen how? Would 2 tools cover the planned interactions? Chapter 12 turns these questions into an explicit allocator.

## Why bigger windows do not solve this

Context windows have grown dramatically, and that is genuinely useful — more evidence fits, more history fits, whole codebases sometimes fit. But it does **not** retire the discipline, for four reasons. Each is a thread the curriculum follows to its end:

1. **Position effects.** Long-context research — most prominently *Lost in the Middle* (Liu et al., 2023; arXiv:2307.03172) — found that retrieval-style performance over long inputs often degrades when the crucial information sits in the middle of the context, with better performance when it appears near the beginning or the end (a roughly U-shaped positional effect in their experiments). The effect's magnitude varies by model and task; Chapter 13 gives you a protocol to measure it on *your* model rather than assume.
2. **Noise costs attention.** More irrelevant context is not neutral — it dilutes and competes with relevant context. Relevance engineering (Chapters 11, 15) exists because "include everything" measurably underperforms "include the right things."
3. **Cost and latency scale with tokens.** Bigger requests cost more and return slower. Chapter 31 makes the economics explicit; Chapter 16 shows why reuse (caching) becomes a first-class design tool at scale.
4. **The window is shared, not personal.** The window does not care that your history "deserves" space — capacity is contested (Chapter 1). A fixed ceiling merely relocates the contest; it does not referee it.

There is also a trust dimension: everything you include is something the model may act on. A window that swallows the whole corpus swallows the malicious document along with the good ones (Chapter 24). Curation *is* a security control.

## How inference uses the context (conceptually)

You do not need transformer internals for this discipline, but two behavioral facts matter for engineering decisions:

- **The whole window is processed on every step.** Nothing is "free" because it was sent last turn; a multi-turn agent pays for its accumulated context on every iteration (Chapters 21, 31).
- **Attention is not uniform.** Models demonstrably weight content differently by position, formatting, and structure — which is why labeling (Chapter 24) and ordering (Chapter 13) are engineering decisions rather than cosmetic ones.

## Worked example: estimating the lab corpus

Open the corpus manifest (`datasets/synthetic/corpus/manifest.json`) and pick a document; run its text through the heuristic estimator (`python -m context_engineering.cli` after Part II, or read `tokens.py` and call it directly). You now know roughly what the *entire* Nimbus Dynamics corpus would cost in a single request versus what a focused eight-chunk assembly costs. Keep those two numbers — they anchor the Chapter 12 budget lab, where you will force trade-offs by shrinking the window and watch the allocator degrade gracefully instead of overflowing.

## Exercises

1. **Beginner** — Estimate (heuristically, no code) the token cost of this chapter as context. Then run it through the library estimator. Compare, and write one sentence about which direction you would adjust the heuristic for markdown-heavy text.
2. **Intermediate** — Construct two renderings of the same fact set — one prose paragraph, one labeled key-value block ("POLICY: 2 remote days/week; SOURCE: hr-remote-work v2; DATE: 2026-08-14") — and estimate both. When would the extra structure be worth its cost, and when not? (Chapter 24 will ask you to revisit this for security.)
3. **Advanced** — Model a 32K-token window application whose history grows 800 tokens per turn. Compute the turn at which unmanaged history alone exhausts the window if evidence needs a 6K floor and output needs 2K. Then sketch two management policies (truncate-last-N vs. rolling summary) and state what each loses.

## Common failures

- **"It fits the window" as the only criterion.** Fitting is necessary, not sufficient; the window is shared with relevance, ordering, trust, and output needs.
- **Estimating with word counts.** Close enough for a napkin; wrong enough to overflow a plan. Use a token heuristic and verify with the provider's tokenizer before committing to fixed limits.
- **Freezing "the" tokenizer.** Tokenizers and limits differ per provider and change over time. Pin exact counts to your specific model version, and re-verify the numbers when models change (Chapter 32: regression detection).
- **Reserving no output budget.** Mid-response cutoffs are a context engineering failure, not a model quirk.

## Summary

- Tokens are sub-word units; ~4 characters or ~¾ word is a heuristic with real variance; whitespace and structure cost.
- Three budgets — input, output, effective working set — must be managed together; exact numbers are provider facts.
- Larger windows don't end the discipline: position effects (Lost in the Middle), noise costs, economics, shared capacity, and trust all keep curation essential.

## Mastery checklist

- [ ] I can explain what a token is and why word counts mislead.
- [ ] I can produce a token ledger for a realistic request from memory, including reserved output.
- [ ] I can argue both directions of "bigger windows make context engineering (less) important" and take a defensible position.

## Review questions

1. Why can't the output budget be treated as "whatever is left over"?
2. Name two rendering choices that change token cost without changing information, and one situation where the more expensive rendering is justified.
3. Summarize the Lost in the Middle finding in one sentence — and state what it does *not* prove.

## References

- Liu et al., *Lost in the Middle: How Language Models Use Long Contexts* (2023) — https://arxiv.org/abs/2307.03172 (reviewed 2026-10-20)
- Anthropic, *Effective context engineering for AI agents* — context-as-finite-resource framing — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (reviewed 2026-10-20)
- Provider tokenizer documentation: consult the current docs of your specific provider before relying on exact counts; provider limits change over time.

## Next

Chapter 3 dissects the request itself: the anatomy of context.

# Chapter 11 — Context Selection and Relevance

> Part III · Dynamic Context Construction
> Prerequisites: Chapter 10 · Status: complete
> Time: ~60 minutes

## Overview

Selection is where "everything that matched" becomes "what the model will actually see." This chapter teaches relevance as a composite decision — query coverage, recency, authority, redundancy, diversity — and confronts the industry's most persistent selection error: treating a retrieval similarity score as ground truth about usefulness. The implementation is `selection.py`; the honest position throughout: selection policies are heuristics that must earn their place on the evaluation harness, never on intuition.

## Why retrieval scores are not enough

A similarity score answers exactly one question: *how much did this text's tokens overlap my query's tokens?* It says nothing about:

- **Whether the chunk answers the question** ("remote" appears in "remote control batteries" too).
- **Whether the chunk is the right *version/instance*** (the highest-scoring remote-work chunk might be the superseded v1 — Chapter 9 made this structural, but only if you wired it).
- **Whether two near-identical chunks are both needed** (they rarely are; redundancy wastes budget and can crowd out coverage).
- **Whether the corpus simply lacks the answer** (all scores low ≠ "use the best wrong one"; it means refuse or escalate).

The failure shape to fear: a confident pipeline that always hands the model *something*, because selection had no concept of "nothing here is good enough." The refusals you engineered in Part 0 depend on selection being allowed to say "insufficient."

## The composite decision

`rank()` in `selection.py` composes four signals into one ordering, then prunes. Reading it alongside this section is the lab-work for this chapter:

1. **Normalized retrieval score.** BM25 scores are query- and corpus-dependent (a 9.2 means nothing across queries); normalizing by the best score in the candidate set makes them comparable *within* one selection decision.
2. **Recency bonus (max 0.15).** All else near-equal, prefer the fresher source. Deliberately a tiebreaker, not a dominator — a *smaller* score gap that freshness can legitimately flip, and a bigger gap it cannot. The unit test pins this behavior on purpose: policy constants encode judgment, and judgment should be testable.
3. **Authority weight (optional, via chunk metadata).** When two sources restate the same fact, the system-of-record should win. This is Chapter 5's authority made mechanical. Default 1.0 — absent explicit authority metadata, selection stays agnostic rather than inventing hierarchy.
4. **Near-duplicate removal, then MMR-style diversity.** Jaccard over keywords (cheap, deterministic) removes redundancy; the diversity pass skips a candidate too similar to one already selected, trading a little per-item relevance for breadth. Why breadth matters: multi-facet questions ("remote work and equipment") die when eight variants of the same sentence fill the window.

Finally, `to_components()` converts the survivors into **UNTRUSTED EVIDENCE** components with rank-mapped priorities — the boundary where Chapter 3's trust rule becomes code: retrieved text is data, whatever its score said.

## Selection limits and the "insufficient" case

A selection policy must be able to return *nothing*. `SelectionPolicy.min_score` exists for that: below a floor of normalized quality, prefer refusal to noise. But min_score is a poor proxy for "no answer exists" — the deeper mechanism is Chapter 27's **evidence coverage** metric: compare required facts against selected content, and refuse when coverage fails. Selection chooses among candidates; *sufficiency checking* decides whether the answer should ship. Conflating them produces systems that answer confidently at score 0.11 because "it was the best we had."

There is also the opposite limit: **over-selection**. More evidence is not safer. Chapter 2's noise-cost and Chapter 13's position effects both bite when selection max_items creeps upward "for robustness." The correct `max_items` is an *evaluation result*, not a comfort level.

## Worked example: one query through the selector

Take "What is the vacation carryover rule?" against the Nimbus corpus with a retrieval k of 10. Candidates: three `hr-vacation` chunks (the carryover section scoring highest), two `benefits-faq` chunks (mentioning allowances), and a stale `data-retention` chunk ("carryover" appears in a retention sense — a real lexical false friend). Watch the selector work: normalization makes the hr-vacation section lead; dedup removes a paraphrase of the same section; diversity keeps one benefits chunk; the retention chunk's normalized score falls below min_score and dies. Output: three components, priorities 2/3/4, all internal-access, current-version — each decision visible in `metadata["selection_rank"]` and the retrieval scores retained for the trace.

Now break it deliberately (this is the intermediate exercise): set `min_score=0` and watch the retention chunk enter context. Nothing crashes; the model now has a wrong-domain "carryover" competing with the real one. That is Chapter 4's taxonomy failure #2 (irrelevant context), introduced by a policy knob — which is why policy defaults must be *justified in tests*, not merely present.

## Exercises

1. **Beginner** — Run the worked example's query through `rank()` with default policy; print rank, composite inputs, and which candidates dedup/diversity removed. Identify the one decision you would have made differently, and note why (this is calibration training, not obedience).
2. **Intermediate** — Add an "insufficiency floor": after selection, compute the fraction of query keywords covered by the union of selected chunks; if below 0.5, return an explicit `SelectionVerdict(insufficient=True)` instead of components. Wire it into the Part 0 refusal behavior and test both sides of the floor.
3. **Advanced** — Implement authority metadata: `authority_weight` per source owner from a small table (people-ops: 1.3 for HR topics, platform-reliability: 1.3 for deployment topics), and *evaluate* it: does it fix any Chapter 8-style misranking on five hand-built queries? Report where composite weights misfire and propose the fix in terms of the four signals.

## Common failures

- **Score worship.** Handing raw scores to the model or to logging as if they were truth values. Scores order candidates; they do not certify answers.
- **Selection without refusal.** No insufficiency mechanism, so the pipeline always ships "the best we found." Users learn to distrust the *confident* answers most.
- **Diversity disabled "because recall matters."** Redundant top-8 that all restate one fact; multi-facet questions fail while metrics look great (each chunk *is* relevant). Coverage metrics (Chapter 27) catch this; relevance metrics alone do not.

## Summary

- Selection composes normalized score + recency tiebreak + authority weight, then dedup and diversity — each signal small, each testable, none sacred.
- A selector that cannot refuse is a liability; sufficiency (coverage) is a separate, later check from relevance.
- Policy constants encode judgment and must live in tests.

## Mastery checklist

- [ ] I can predict each stage's effect on a candidate list and verify with `rank()`.
- [ ] I can explain why recency is capped at tiebreaker strength, with the test that proves it.
- [ ] I can implement an insufficiency floor and argue its threshold from evidence, not vibes.

## Review questions

1. Why normalize retrieval scores per-selection instead of using raw BM25 values?
2. Give a query where diversity *hurts* correct answers — what does that tell you about max_items?
3. Why is coverage a *separate* check from relevance, and what failure shape does conflating them produce?

## References

- Carbonell & Goldstein, *MMR* — the diversity mechanism adapted — (reviewed 2026-10-20)
- Implementation: `src/context_engineering/selection.py`; tests `tests/unit/test_selection.py`.

## Next

Chapter 12: the budget — what fits when everything doesn't.

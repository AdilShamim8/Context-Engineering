# Part III — Dynamic Context Construction

> Chapters 10–16 · Prerequisites: Part II · Outcome: candidates in, a budgeted/ordered/labeled model request out — every decision recorded.

## Chapters

| # | Chapter | Focus | Code |
|---|---|---|---|
| 10 | [The Context Engineering Lifecycle](chapter-10-lifecycle.md) | The 12-step loop; pipeline skeleton | `pipeline.py` |
| 11 | [Context Selection and Relevance](chapter-11-selection.md) | Composite ranking, dedup, diversity, refusal | `selection.py` |
| 12 | [Context Budgeting and Allocation](chapter-12-budgeting.md) | Priorities, truncation, reserved output, reports | `budget.py` |
| 13 | [Context Ordering and Position Effects](chapter-13-ordering.md) | Lost in the Middle, strategies, measurement protocol | `assembly.py` |
| 14 | [Context Compression and Summarization](chapter-14-compression.md) | The ladder; pinned facts; loss budgets | `compression.py` |
| 15 | [Progressive Context Disclosure](chapter-15-progressive-disclosure.md) | Pointers, on-demand fetch, per-call authorization | `tools.py` (Part V) |
| 16 | [Context Caching, Reuse, Invalidation](chapter-16-caching.md) | Fragments, retrieval cache, prefix property | patterns |

## The part's single idea

Between "a governed pile of candidates" and "a model request" stands a chain of decisions — *select, budget, order, compress, or defer* — and this part's position is that **each decision must be explicit, policy-driven, recorded, and testable**. The alternative, practiced widely, is a string that grew by accretion and debugged by superstition.

## Completion criteria

- [ ] You can build a Pipeline whose stages map 1:1 to lifecycle steps, with a degradation ladder.
- [ ] You can read an allocation report and trace any lost content to a policy line (Ch. 12).
- [ ] You can predict selection behavior (dedup/diversity/recency) and its failure modes (Ch. 11).
- [ ] You can demonstrate mechanical position loss and spec the model-dependent protocol (Ch. 13).
- [ ] You can beat truncation with compression on the same budget, with pinned facts surviving (Ch. 14).

Next part: [Part IV — Memory and State](../04-memory-and-state/).

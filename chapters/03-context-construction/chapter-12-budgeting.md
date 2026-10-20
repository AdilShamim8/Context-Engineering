# Chapter 12 — Context Budgeting and Allocation

> Part III · Dynamic Context Construction
> Prerequisites: Chapters 2, 10 · Status: complete
> Time: ~70 minutes

## Overview

The budget forces every abstract priority into a concrete, token-denominated decision: **what fits, in what order of precedence, and what happens to what doesn't.** `budget.py` implements a policy-driven allocator with an audit trail, and this chapter teaches you to read its allocation reports the way a financial controller reads a ledger — every inclusion, exclusion, and truncation must be explainable and defensible. This is also the chapter where the three budgets from Chapter 2 (input, output, effective working set) become one coherent data structure.

## The ContextBudget: three reservations before any content

```
available_for_context = total − reserved_output − safety_margin
```

- **Reserved output** is non-negotiable. The classic production failure — mid-generation cutoffs — traces to allocating 100% of the window to input and hoping the answer is short. Hope is not a budget line.
- **Safety margin** absorbs estimate error (Chapter 2: heuristics are planning tools) and provider-side framing overhead. When your exact tokenizer says the request fits with 12 tokens to spare, the margin is what saved you.
- Everything left is what the allocator may spend. Default `8192/1024/128` yields 7040 — read the defaults as a *policy statement*, not a constant: an application with long structured answers reserves more; a classifier reserves less.

## The allocation policy, in precedence order

`allocate()` runs a deterministic policy you can recite:

1. **Instructions first, and they must fit.** If instructions alone exceed available space, that is a `BudgetError`, not a graceful-degradation situation — a request whose *instructions* got truncated mid-rule is a request the model will misinterpret in ways indistinguishable from success. Fail loud (Chapter 30).
2. **Everything else by priority** (0 = most important; stable within equal priorities). Priority is set upstream — selection ranks evidence (Chapter 11), history management pins constraints (Chapter 17), tool definitions come from the app. The allocator never invents importance; it executes declared importance.
3. **Fit → include.** Simple case.
4. **Doesn't fit, truncatable kind, remaining ≥ 32 tokens → head-truncate with a visible marker.** Truncation is not silent: ` …[truncated to fit context budget]` appears in the text, the component's token cache resets, and the record says `truncated` with before/after counts. Evidence, memory, history, tool results, and derived content are truncatable; instructions and state are not.
5. **Else → drop, with a recorded reason.** `dropped` records carry `needed X, Y left (priority N)` — the exact sentence you want in front of you when Chapter 4 asks "which family is this failure?"

The result object is the deliverable: `selected` components (safe to assemble, never exceeding available), plus a `report()` that renders every candidate's fate. **Allocation reports are the primary debugging artifact for "excessive length" and "lossy transformation" failures** — you do not debug budgets with print statements; you read the report.

## Why truncation keeps the head (and when that's wrong)

Head-truncation is the default because most document genres front-load their claims (policy: the rule, then details; runbook: steps, then notes). But head-first is a *genre assumption*: changelogs, error traces, and status updates bury the payload at the tail. This is exactly why truncation is a *policy parameter* (kind-dependent, marker-visible), not a hard-coded `text[:N]` — and the advanced exercise has you implement a tail-aware policy and watch Chapter 28's ablation measure the difference.

## No arbitrary percentages

You will meet "the 30/20/50 rule" style folklore (30% instructions, 20% history, 50% evidence). Reject it: **allocation depends on the task, the model, the evidence requirements, and the corpus.** A citation-heavy QA task needs evidence share; a multi-turn refinement task needs history share; a tool-heavy agent needs definition share. The defensible method in every case is the same: build a realistic token ledger (Chapter 2's worked example), set priorities and reservations from the *task*, then let the evaluation harness (Chapter 27) compare allocations — and re-check after any model or corpus change. The allocator gives you the knob; the harness, not the internet, sets the values.

## Worked example: reading an allocation report under pressure

Take the Chapter 11 selection (three evidence components, priorities 2–4), add a 6-turn history (~1200 tokens, priority 1), instructions (~350, priority 0), and a big tool result (~900, priority 5, truncatable). Budget: 4096 window, 800 reserved output, 128 margin → 3168 available.

```text
Budget: 4096 total, 800 reserved output, 128 margin → 3168 available
ID                       KIND            PRI ACTION    TOKENS       REASON
instructions             instruction     0   included  350/350
history-recent-6         history          1   included  1204/1204
hr-vacation-c03          evidence         2   included  198/198
benefits-faq-c01         evidence         3   included  175/175
hr-remote-work-v2-c01    evidence         4   truncated 132/590      truncated from 590 tokens to fit remaining space
tool-result-calendar     tool_result      5   truncated 47/907      truncated from 907 tokens to fit remaining space
```

Read it like a controller: history took 38% of context — did six full turns earn that versus compressed notes (Chapter 14)? Two truncations kept *head* content — was the tail where the answer lived? The remaining-space floor (32) is why nothing was dropped outright — raise history priority carelessly and the first *drop* appears, and the report tells you whose budget it ate. Every "the model ignored the policy section" debugging session should start at this table, not at the prompt.

## Exercises

1. **Beginner** — Reproduce the worked example's report with the library (build the components yourself). Then lower `total_tokens` by 500 and identify precisely who lost space and why.
2. **Intermediate** — Your PM insists history matters more than fresh evidence. Flip priorities and produce both allocation reports. What *category* of failure does the flip make more likely? Write the golden case that detects it (Chapter 28 previews the mechanics).
3. **Advanced** — Implement kind-aware truncation policy: `TOOL_RESULT` truncates tail-first (recent output usually matters most), evidence stays head-first. Add the unit tests, then measure on the eval suite: construct two questions where the difference should show, and report whether it does.

## Common failures

- **No reserved output.** Requests "fit," answers cut off mid-sentence; team blames the model. The report would have shown 0 reserved.
- **Silent truncation.** Provider-side or string-slice truncation with no marker: the model cites half a sentence, the user trusts the citation. Visible markers are a correctness feature.
- **Priority theater.** Every component marked priority 0 "because it matters." The allocator degrades to insertion order; the report exposes this instantly (look for uniform priorities).
- **Debugging budgets by prompt.** When something didn't fit, the answer is in the allocation report — never in prompt wording.

## Summary

- Budget = total − reserved output − margin; the allocator executes declared priorities with instructions-first, visible truncation, and reasoned drops.
- Head-truncation is a genre assumption; policies are parameters; reports are the debugging artifact.
- Percentage folklore is rejected; the harness sets allocation values, per task, and re-checks them.

## Mastery checklist

- [ ] I can produce and read an allocation report, tracing any lost content to a named policy line.
- [ ] I can explain why instruction overflow is an error while evidence overflow is degradation.
- [ ] I can design a budget for a given task from a token ledger, and say how the harness would validate it.

## Review questions

1. Why is `MIN_TRUNCATED_TOKENS = 32` a real policy (what breaks below it) rather than an arbitrary constant?
2. What does a uniform-priority allocation report reveal, and what upstream mistake produces it?
3. Which budget line does Chapter 31 (cost) most directly attack, and how?

## References

- Implementation: `src/context_engineering/budget.py`; tests `tests/unit/test_budget.py`.
- Chapter 2 (token estimation limits), Chapter 14 (compression as the upstream alternative to truncation), Chapter 31 (the economics).

## Next

Chapter 13: order — the same components, differently arranged, measurably different behavior.

# Chapter 17 — Conversation History and Short-Term Context

> Part IV · History, Memory, and State
> Prerequisites: Part III · Status: complete
> Time: ~50 minutes

## Overview

Conversation history is the component most applications manage by accretion: append every turn, hope the window holds, truncate when it doesn't. This chapter treats history as a budgeted, policy-managed component like any other — and implements the three mechanisms that make it manageable: a bounded recent-turns window, deterministic rolling summaries of dropped turns, and pinned constraints that must survive any window. The implementation is `history.py`; the running question is the one Chapter 12's worked example raised: *is the recent window earning its tokens?*

## Why raw history underperforms

Unbounded history fails in three distinct ways, and it is worth being able to name them separately:

1. **Economic failure.** Every token of history is re-sent — and re-paid — on every turn (Chapter 2: the whole window is processed every step). A 20-turn support chat can quietly become 80% history by cost, with the evidence for the *current* question squeezed into the remainder. The allocation report makes this visible; nothing else will.
2. **Quality failure.** Old turns are not merely irrelevant — they are *actively misleading*: a user's address from turn 2 superseded in turn 9, a requirement stated then retracted, an error the assistant itself made and the conversation moved past. All of it competes with the present, and Chapter 13 tells you position matters for what wins that competition.
3. **Privacy failure.** History accumulates *everything said*, including content later regretted. Deletion has to mean something (Chapter 25) — which requires knowing where history lives: the window, the archive, and the rolling summary are three different artifacts with three different retention stories.

## The managed window: three mechanisms

`ConversationHistory` implements the pattern that resolves all three failures at once:

- **`max_turns`** — the live window. Old turns move to an *archive* (not deleted: needed for summaries and audit) — the window is what enters the request.
- **`dropped_summary()`** — a rolling summary of the archive, built with `structured_notes` (Chapter 14 rung 5: deterministic, schema-shaped, inspectable). In `to_components()` this ships as a **DERIVED** component, explicitly labeled "compressed" — the compression must be visible in the request, not silently assumed to be the conversation.
- **`pin()`** — constraints and facts that must survive any window ("budget: 50 words", "the user is on the Standard plan"). Pinned items ship as their own component at the highest history priority.

The critical design read: **history is now three components** — pinned constraints, rolling summary, live window — each individually budgetable, each with its own trust and retention semantics. "History" as one blob is exactly what this module exists to prevent.

## How much window is enough?

The honest answer is empirical, per task. The diagnostic method: run the same question set with `max_turns` at 2, 6, 12, and unbounded, and score with the Chapter 27 harness. Two patterns typically emerge: for *task-focused* chats, most value lives in the last few turns (older turns mostly restate context that a summary carries more cheaply); for *long-running advisory* chats, the value is in constraints and commitments — which belong *pinned*, not in a longer window. The trap is choosing `max_turns` by taste: it is a budget parameter like any other, and Chapter 12's ledger method applies to it unchanged.

## Statefulness and its illusion

"Stateless API" meets "feels stateful conversation" through exactly this machinery: the *server* holds nothing; the application reconstructs each request from (history store + memory store + task state). That framing pays off twice: Chapter 19's checkpoints become trivial (serialize what we already manage), and the "who can see what" question (Chapter 25) has a precise answer — whatever the three history artifacts contain, nothing else.

## Worked example: a 30-turn chat under a tight budget

Simulate 30 varied turns with two pins added early ("answer in under 50 words", "the deployment is Friday"). With `max_turns=6` and the Chapter 12 budget, the history components total: pinned ~30 tokens, summary ~90 tokens (15 archived turns compressed), live window ~180 tokens. Same chat unbounded: ~1,400 tokens and rising. The allocation report shows both; the live question's evidence fits comfortably in one and gets truncated in the other. Then the interesting check: which *facts* did the summary keep? The deployment-Friday commitment survived (pinned, bullet-style); the user's aside about lunch plans did not. That is rung-5 schema myopia in action — and the reason summaries are labeled DERIVED and spot-auditable (Chapter 28).

## Exercises

1. **Beginner** — Run the worked example. Adjust `max_turns` until the live window alone exceeds your evidence allocation. State the trade you would *not* make and why, in budget terms.
2. **Intermediate** — Implement selective retention: keep turns containing constraint markers (*must*, *don't*, *deadline*, numbers) in the window beyond `max_turns`, demote the rest to the archive. Write the test proving a *must* turn survives turn 40 of a flood.
3. **Advanced** — Build the history ablation: question set × {pinned+summary+window, summary+window, window-only} on a 20-turn scripted chat where the correct answer depends on one early constraint. Report where each configuration loses it — and read the assembled contexts to see exactly which artifact failed to carry the constraint.

## Common failures

- **The eternal window.** No bound; costs grow linearly; evidence dies by squeeze. The allocation report is the detection tool.
- **Truncation amnesia.** Dropping old turns *without* a summary loses constraints silently — the classic "assistant forgot I'm vegetarian" failure. The summary mechanism exists precisely to carry commitments forward.
- **Pin-everything inflation.** Pinning 12 notes per chat recreates the unbounded problem in a new component. Pins are for *standing constraints*, not facts-of-the-week.

## Summary

- Raw history fails economically, qualitatively, and privately; the cure is three managed components: pinned constraints, rolling summary, bounded window.
- Summaries are deterministic, labeled DERIVED, and spot-auditable — compression is never silent.
- Window size is a budget parameter chosen by ablation, not taste; statelessness plus managed history equals statefulness with an exact privacy surface.

## Mastery checklist

- [ ] I can compute what a 30-turn chat costs with and without management, from a real allocation report.
- [ ] I can explain each of the three history components' trust/retention semantics.
- [ ] I can build the history ablation and interpret which artifact failed.

## Review questions

1. Why is the rolling summary a DERIVED component rather than HISTORY?
2. What does "deletion" have to answer for, given history lives in three artifacts?
3. When does a *longer* window make answers worse, not just costlier?

## References

- Implementation: `src/context_engineering/history.py`; tests `tests/unit/test_history.py`.
- Anthropic, *Effective context engineering for AI agents* — compaction and note-taking across agent steps — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (reviewed 2026-10-20)

## Next

Chapter 18: persistent memory — what the application remembers *between* conversations.

# Part IV — Conversation History, Memory, and State

> Chapters 17–19 · Prerequisites: Part III · Outcome: the request's three persistence layers — said, remembered, and working — each managed, auditable, and reconstructible.

## Chapters

| # | Chapter | Focus | Code |
|---|---|---|---|
| 17 | [Conversation History and Short-Term Context](chapter-17-history.md) | Bounded windows, rolling summaries, pinned constraints | `history.py` |
| 18 | [Persistent Memory Engineering](chapter-18-memory.md) | Kinds, extraction, conflicts, TTL, deletion, audit | `memory.py` |
| 19 | [Structured State, Checkpoints, and Recovery](chapter-19-state.md) | Three-artifact separation, minimum-viable resume, drift recovery | patterns; `orchestrator.py` (Part V) |

## The part's single idea

"Stateless model" + "stateful product" = three deliberately different persistence layers: **history** (what was said — bounded, summarized, never unbounded), **memory** (what the application chose to remember — sourced, audited, expirable, deletable), and **state** (where the work is — decisions and pointers, re-deriving context on resume). Teams that fuse these into one "assistant memory" blob get products that are simultaneously forgetful about the right things and clingy about the wrong ones.

## Completion criteria

- [ ] You can size a history window from an ablation, not taste, and show the three history components in an allocation report.
- [ ] You can demonstrate a numeric memory conflict being flagged and superseded, with the audit trail proving it.
- [ ] You can design a checkpoint that survives the resume-with-everything-else-empty acid test.

Next part: [Part V — Tools, Agents, and Multimodal Context](../05-tools-agents-multimodal/).

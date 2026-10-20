# Chapter 18 — Persistent Memory Engineering

> Part IV · History, Memory, and State
> Prerequisites: Chapter 17 · Status: complete
> Time: ~70 minutes

## Overview

History is what was *said*; memory is what the application *chose to remember*. This chapter covers the deliberate version of that choice: what kinds of memory exist, how memories get in (extraction), how conflicts are handled (flagged, never silently resolved), how they age and expire, and how they are deleted — with an audit trail through it all. `memory.py` implements the store; the Chapter 18 lab drives it into the failure modes so you can watch them happen on purpose.

## Why persistent memory — and why carefully

Done well, memory is the difference between an assistant that knows your constraints on the second conversation and one that asks everything twice. Done carelessly, memory is a new class of liability: wrong facts that outlive their correction (a promotion remembered as a role change, an address that was never updated), inferences that harden into "facts," stale records that silently shadow fresh evidence, and deletion requests that delete nothing because copies live in three subsystems. The industry's honest summary: memory multiplies both value and blast radius.

## The taxonomy (with the caveat Chapter 18 of the curriculum promised)

Four working kinds, useful rather than canonical — treat them as *schema categories for your audit trail*, not a scientific ontology:

| Kind | Example | Typical source | Typical TTL |
|---|---|---|---|
| `fact` | "User's team is Platform Reliability" | user-stated | none / explicit |
| `preference` | "User prefers concise answers" | user-stated | none |
| `episodic` | "User's ticket ESC-4471 was resolved 2026-10-02" | system/inferred | short (months) |
| `task_note` | "Deployment is blocked on the flag expiry" | current task | task lifetime |

The column that matters most is **source**: `user-stated` facts deserve high trust; `inferred` memories (the model *concluded* something) carry their provenance and a confidence score — because an inferred memory that hardens into an un-labeled "fact" is a hallucination with persistence.

## Extraction: what earns a place

The extraction decision is a selection problem (Chapter 11's discipline transposed): most utterances should *not* become memories. Signals worth persisting: explicit corrections ("no, it's Platform Reliability, not Data"), stable preferences, commitments and constraints with duration ("we deploy Fridays"), and identifiers the user will reference later. Signals to refuse: transient state ("I'm tired today" — episodic at best), guesses, and anything sensitive that has no demonstrated task value — because Chapter 25's minimization principle applies to memory first of all: *the cheapest memory incident is the one you declined to store.*

## Conflicts: flag, never flip a coin

The store's `detect_conflicts` catches the two highest-stakes patterns: overlapping memories whose numbers differ (`numeric_mismatch` — the stipend was 300, now 150: which is true?) and overlapping memories that simply disagree (`overlapping_content_differs`). The design rule that matters: **the store flags and records; it does not resolve.** Resolution is a policy decision — supersede (the new record carries `supersedes: old_id`), keep-both-labeled (let retrieval surface both with provenance), or refuse-and-ask. What is forbidden is the default non-policy: both memories coexist, retrieval returns whichever scored higher for the query, and the answer alternates between sessions. That is Lab 00 scenario 3 with persistence.

## Expiration, supersession, and deletion

- **TTL (`ttl_days`)** — memories with a shelf life (incident numbers, project states) expire and *stop matching retrieval* even before purge — expired records are invisible at retrieval, not merely marked.
- **Supersession** — explicit, machine-readable (`supersedes`), inherited from Chapter 9's versioning logic; the difference here is the *application* is doing the superseding.
- **Deletion** — `delete(reason)` and `delete_all(reason)` write the reason to the audit trail. A deletion without an audit record is a compliance bug (Chapter 25/26); a deletion that leaves rolling summaries, caches, or trace exports containing the deleted memory is a *silent leak* — the advanced exercise makes you hunt your own system for copies.

## The audit trail as first-class output

Every insert, replace, conflict, purge, and delete writes an audit event. This is not logging for debugging — it is the *product requirement* of a system that remembers things about people: "show me what you know about me and where it came from" (Chapter 26's transparency) is a query over this trail plus the store. `to_state()`/`from_state()` carry both, because an unauditable memory file is unauditable in exactly the way the security chapters forbid.

## Worked example: three conversations, one memory store, one conflict

Session 1: "Save it: the wellness stipend is 300 dollars a quarter" → `fact`, user-stated. Session 2 (months later): "By the way, the stipend went up — it's 400 now" → `upsert` returns `numeric_mismatch` against the old record. The developer's chosen policy: supersede — new record carries `supersedes: r1`, old stays in the audit trail for transparency. Session 3: "What's my stipend?" → retrieval returns the current record *only*; the answer cites its provenance and its supersession chain is one audit query away. Now rerun it with the non-policy (keep both, no flags): the answer flips depending on keyword scores between sessions. The store didn't change; the policy did. **Memory behavior is policy made durable** — that sentence is the chapter.

## Exercises

1. **Beginner** — Reproduce the worked example both ways (supersede vs. default non-policy). Print the audit trail after each session and annotate each event.
2. **Intermediate** — Implement memory extraction for the assistant: after each conversation turn, propose candidate memories (deterministically: regex for corrections/numbers/commitments behind a proposal function), but store only candidates passing a minimization checklist you write. Report precision over a 20-turn script: how many proposals were correct, how many would have been liabilities?
3. **Advanced** — The copy-hunt: after deleting a memory, search the *whole system* (history archive, rolling summary, tool results, trace exports) for its content. Write the deletion checklist that finds every copy, and the one-paragraph design argument for where deletion boundaries must live to make "delete" mean delete.

## Common failures

- **Inference hardening.** Model-inferred "facts" stored without source labels; later indistinguishable from user statements. The `source` and `confidence` fields exist to prevent exactly this.
- **Conflicting memories, silent arbitration.** Highest-scoring memory wins per query; users see a system that "can't keep its story straight."
- **Immortal memories.** No TTL policy anywhere; episodic trivia accumulates into a permanent, slow-motion privacy problem.
- **Deletion theater.** Deleting the record while summaries, caches, and exports keep its text — the copy-hunt failure above.

## Summary

- Memory = policy made durable: kinds with sources, extraction with minimization, conflicts flagged not resolved, TTL/supersession/deletion with reasons, all audited.
- Inferred memories carry provenance and confidence or they don't belong in the store.
- The blast radius rule: memory multiplies value and liability together; the store's design must make the second visible.

## Mastery checklist

- [ ] I can design an extraction rule that declines more than it stores, with reasons.
- [ ] I can demonstrate a numeric conflict being flagged, then superseded, with the audit trail proving both.
- [ ] I can define, for a given product, the deletion boundary set that makes "forget me" complete.

## Review questions

1. Why does the store flag conflicts rather than resolving them? Name the failure mode forbidden by that choice.
2. What belongs in the `source`/`confidence` fields of an inferred memory, and what downstream behavior do those fields gate?
3. Why are expired records invisible at retrieval rather than merely marked?

## References

- Implementation: `src/context_engineering/memory.py`; tests `tests/unit/test_memory.py`.
- OWASP LLM Top 10 — sensitive-information disclosure and memory-related risks — https://owasp.org/www-project-top-10-for-large-language-model-applications/ (reviewed 2026-10-20)

## Next

Chapter 19: task state — the third thing that persists, and how interrupted work resumes safely.

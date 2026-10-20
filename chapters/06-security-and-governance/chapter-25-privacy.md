# Chapter 25 — Privacy, Multi-Tenancy, and Sensitive Information

> Part VI · Security, Privacy, and Governance
> Prerequisites: Chapters 9, 18, 24 · Status: complete
> Time: ~60 minutes

## Overview

Chapter 24 defended the context against *adversarial* content; this chapter defends it against *accidental disclosure* — the quieter, statistically more common disaster. The problem statement is short: context assembly is a machine for putting information in front of a model, and *every stage of that machine* — retrieval, memory, caches, tool results, traces — is a place where data about one person can surface in another person's answer. This chapter covers the minimization principle, tenant isolation, cache/memory boundary design, log redaction, and what deletion has to mean. All examples stay synthetic; the incidents you are about to prevent look exactly like the tests you will read.

## The minimization principle: collect and include the least

Every stage of the lifecycle inherits one rule — **data minimization, applied twice**: store the least you need, and place the least of what you stored into any model context. The reasoning is asymmetric risk: information you never carried cannot leak, cannot be subpoenaed, cannot be mis-scoped by a future bug, and cannot haunt a Chapter 18 deletion request. Concretely, for context engineering:

- **Don't retrieve what the task doesn't need.** Chapter 11's selection is a privacy control in disguise; max_items and min_score cap the surface, not just the budget.
- **Don't remember what has no task value.** Chapter 18's extraction discipline ("decline more than you store") is the first line of privacy defense — the wellness-stipend complaint that never becomes a memory can never be retrieved into the wrong answer later.
- **Don't log what you assembled.** Traces capture *decisions and structure* (what was included, why) — redacted of content by default (Chapter 29). The assembled request is the most sensitive artifact in your system; it should exist in memory for the request's lifetime and nowhere after.

## Tenant isolation: one mechanism, enforced three times

Multi-tenancy is the same Chapter 9 access-control idea with higher stakes: the corpus, the memory, and the caches each hold per-tenant content, and the invariant is that **tenant A's request can never see tenant B's material** — not in results, not in rankings, not in traces. The repository's mechanism (access policies as predicates, applied before ranking) extends verbatim: make tenant id part of the policy, apply it in every one of the three places data waits:

1. **Retrieval.** The predicate filter (Chapter 7/9) — tenant id in the key/predicate, before scoring, always. The classic bug class: filtering *after* ranking (Chapter 9's k-truncation leak) or filtering the document search but not the *memory search* — two doors, one bolted.
2. **Memory.** `MemoryStore.retrieve(access_policy=...)` filters, and records carry per-user access classes — the Chapter 18 store already behaves this way (a restricted note is invisible to an internal query). Personal memory is tenant data with n=1; every Chapter 18 rule applies, plus deletion semantics (below).
3. **Caches.** Chapter 16's rule, worth its own repetition: **the cache key contains the tenant/access identity** — `(query, corpus_version, policy, tenant)`. A cache key without the policy is a pre-built cross-tenant leak that fires on identical questions. The failure is silent: both users get *plausible* answers.

A second-order hazard worth naming: **shared caches and shared prompts**. Global cache entries and giant shared system prompts feel efficient and leak *shape* — error messages that quote another tenant's document id, timing differences, or in the worst case the content itself. Shared anything across a trust boundary needs the same key discipline.

## Sensitive content in context: the exposure budget

When a request *legitimately* handles sensitive content (an HR case, a security incident), the context engineer's question is: **who else will see this request?** — because the answer is not "nobody": traces, caches, checkpoints (Chapter 19!), error reports, and the provider's own logging all touch the assembled request. The design patterns, each already built in this curriculum, now assemble into a checklist:

- Access-filter *before* assembly (the model never holds what the user can't see — Chapter 9).
- Screen and wrap sensitive-as-untrusted if it came from outside (Chapter 24 cuts both ways).
- Keep checkpoints as decisions-and-pointers, never content dumps (Chapter 19) — state is the least legitimate place for sensitive accumulation.
- Redact traces by default (Chapter 29's rule); store findings and reasons, not payloads.
- Prefer derived representations over raw sensitive text when the task allows (Chapter 23's derivation logic, now a privacy tool: "the stipend is $300" is a fact; the complaint email is a document).

## Deletion: what "forget me" has to mean

Deletion in a context system is a *boundary design* problem, not a `DELETE` statement. The data multiplies: the memory record (deletable — Chapter 18 audits it), its copies in rolling summaries and history archives (Chapter 17's copy-hunt), cached retrieval results (Chapter 16), checkpointed state (Chapter 19), traces (Chapter 29), and the answer outputs that quoted it. A deletion that misses any surface is silent non-compliance — the user believes the fact is gone; a correlated query two days later proves otherwise.

The engineering answer is boundaries, not hunts: define the surfaces where content may persist, design each with TTLs or reference-only storage, and make the deletion checklist a *test* — the Chapter 18 project's copy-hunt drill generalized. The most robust design decision available: **store pointers, not content, everywhere downstream of the memory store** — then deletion is one operation plus cache invalidation, and the hunt reduces to the store itself.

## Worked example: the almost-incident

A support assistant serves two tenants on one corpus platform. Tenant Acme's admin edited their policy doc; tenant Globex's user asks a policy question. The bug: retrieval cached per query with a 24-hour TTL, no tenant in the key. Both asked "what's the approval deadline?" — Globex's answer quotes Acme's freshly-cached chunk, with Acme's internal doc id in the citation. Nobody breached anything; the *cache key* did. The forensic trail (with proper traces): identical cache hit ids across two tenant-scoped requests, one line of evidence. The fix is one key field plus invalidation tests — and the test-first version is: *write the test that fails against a tenant-less cache key before you write the cache.* That inversion — test the invariant, then build — is Part VII's whole philosophy arriving in Part VI.

## Exercises

1. **Beginner** — Extend `AccessPolicy` with tenant ids (as the Chapter 9 advanced exercise) and write the three-door test: retrieval, memory, and cache all return empty for tenant A asking about tenant B, from a corpus fixture with two tenants.
2. **Intermediate** — Build the exposure-budget checklist for an HR-case assistant: for each artifact (request, trace, cache, checkpoint, memory, output), state what sensitive content may appear there and which existing mechanism bounds it. Find the artifact your design *left open* — everyone finds at least one; the honest deliverable is naming it.
3. **Advanced** — Implement pointer-only downstream storage: memory keeps content; history, caches, checkpoints, and traces hold ids. Then run the deletion drill: delete one memory, re-run every surface's tests, and prove from test output that zero copies remain. Report every surface that required a code change (that list is the real cost of deletion done right).

## Common failures

- **Post-ranking tenant filter.** Chapter 9's leak, at organizational scale.
- **The unkeyed cache.** The worked example; the most common real-world multi-tenant LLM incident shape.
- **Memory without deletion semantics.** Features that remember but can't forget — a compliance debt accruing interest (Chapter 18's copy-hunt cost, discovered at audit time).
- **Traces that archive the request.** "Full request logging for debuggability" is a data warehouse of user content wearing a debugging costume.

## Summary

- Minimize twice: store less, include less; selection and extraction are privacy controls, not just quality ones.
- Tenancy is access control enforced at three doors — retrieval, memory, caches — with the identity in every key/predicate, before ranking.
- Deletion is boundary design: pointers-not-content downstream makes "forget" one operation; any surface you didn't design for is a surface you'll discover in an audit.

## Mastery checklist

- [ ] I can recite the three doors and design the key/predicate for each.
- [ ] I can run the exposure-budget exercise and find the open artifact in my own design.
- [ ] I can implement pointer-only storage and prove a deletion left zero copies.

## Review questions

1. Why is "filter before ranking" a *privacy* rule and not only an authorization rule? What extra does it prevent in multi-tenant systems?
2. Which artifact is the most sensitive in a context system, and what two design rules protect it?
3. Why do pointers-not-content and Chapter 16's cache keys combine to make deletion tractable?

## References

- OWASP LLM Top 10 — sensitive-information disclosure category — https://owasp.org/www-project-top-10-for-large-language-model-applications/ (reviewed 2026-10-20)
- Implementation: `provenance.py` (policies), `memory.py` (per-record access, deletion audit), `security.py` (redaction), `tests/unit/test_memory.py` (access-filtered memory retrieval).

## Next

Chapter 26: governance — proving, after the fact, what the system did and why.

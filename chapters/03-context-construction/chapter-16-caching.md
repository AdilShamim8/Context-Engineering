# Chapter 16 — Context Caching, Reuse, and Invalidation

> Part III · Dynamic Context Construction · *Optional on first pass*
> Prerequisites: Chapter 12 · Status: complete
> Time: ~50 minutes

## Overview

Caching is how context stops being rebuilt from scratch on every request. This chapter distinguishes the four cache layers a context system actually has, then focuses on the two you control directly: **retrieval caching** (skip re-searching) and **reusable fragments** (skip re-computing assemblies). Provider-side prompt caching is covered as a *concept with a verify-before-rely rule*, because its mechanics, pricing, and even existence change per provider and over time. The chapter's second half is the part most teams skip: invalidation, isolation, and the security mistakes caches enable.

## The four layers

| Layer | What is reused | Key risk | Owner |
|---|---|---|---|
| **Application fragment cache** | Assembled instruction blocks, tool schemas, static components | Staleness after code/policy change | You |
| **Retrieval cache** | Ranked results per (query, corpus-version, policy) | Serving stale corpus; cross-tenant key collisions | You |
| **Provider prompt cache** | The provider reuses processing for identical request prefixes | Mismatched assumptions about what "identical" means; pricing traps | Provider (verified per docs) |
| **Model/context serving infrastructure** | KV reuse etc. | Invisible to you | Provider |

**Provider prompt caching, conceptually:** many providers reuse computation when a request's *prefix* matches an earlier one, making repeated long static prefixes dramatically cheaper and faster. What matters for your architecture: the cacheable unit is the **prefix**, byte-identical, from position zero — so cache-friendliness is an *assembly-order property*: static content (instructions, tool schemas) must come first, and anything per-user must come after. This is why Chapter 13's KIND_GROUPED default is also the cache-friendly default. But — the verify-before-rely rule applies doubly here: which models support it, what the minimum cacheable length is, how prices are metered, and what invalidates a prefix are provider facts that change; check current documentation before baking assumptions into budgets (Chapter 31 prices this in).

## Retrieval caching: the key IS the policy

The retrieval cache's design lesson: **the cache key must contain everything that can change the answer.** Minimum: `hash(query, corpus_version, access_policy, freshness_policy, k, chunking_config)`. Leave out the access policy and you have built a cross-tenant leak: tenant A's search results served to tenant B because the query matched. Leave out corpus_version and you have built Lab 00 scenario 3 as a service: cached v1 answers outliving their supersession. This is Chapter 9's "fail closed, filter first" discipline transposed into cache keys: *the key encodes authorization; the cache never out-ranks governance.*

TTLs are the honest answer to staleness: retrieval caches should expire on corpus events (re-ingestion, version bumps) and on a time floor (documents with effective dates make TTL ≈ expected change cadence). Event-driven invalidation beats pure time-based where you own ingestion: the moment v3 lands, v2's cached results die — no TTL guesswork.

## Reusable fragments

The fragment cache: precompute and version the expensive statics — instruction blocks with pinned policies, rendered tool schemas, compressed corpus overviews (Chapter 15 directories), standardized disclaimer/state headers. Rules: fragments are **content-addressed** (hash of the source material + rendering version), so shipping a new policy text yields a new hash and no stale fragment can survive; fragments carry the same `SourceRef` provenance as live content, so citations and audits (Chapter 26) work identically for cached and fresh material. What you gain: consistent assembly (identical fragments across requests), measurable budgets (fragment tokens are known constants), and provider-cache-friendliness (stable byte-identical prefixes).

## Caching and correctness: the three invariants

1. **Authorization isolation.** No cache entry may ever be readable across access contexts. If your key lacks the access policy, you have a Chapter 25 incident pre-built.
2. **Staleness bounds.** Every entry carries an expiry event (corpus version change) or TTL; nothing lives forever "because it's just a cache."
3. **Redaction before storage.** Traces and cached assemblies may contain user content; caches inherit the log rules (Chapter 29): redact before persist.

## Worked example: caching the assistant's corpus directory

The Chapter 15 directory — access-filtered, one pointer per document — is the perfect fragment: expensive to build (filter + compress per doc), cheap to key `(corpus_version, access_levels, compression_config)`, and static between ingestions. Cache it; watch three questions in a row reuse it; then bump `hr-vacation` to v4 in the manifest and re-ingest: the corpus_version changes, the old directory dies, the next request rebuilds. That sequence — reuse, invalidate, rebuild — is the whole chapter as a lab, with the trace (Chapter 29) showing the cache hits as zero-cost stages.

## Exercises

1. **Beginner** — Write the cache key for a retrieval cache serving the Nimbus corpus. List each key component and the failure its omission causes.
2. **Intermediate** — Implement the directory fragment cache: content-addressed, event-invalidated on corpus version. Prove with a test that editing a corpus document invalidates the fragment, and that an internal-policy user can never retrieve the restricted-policy user's fragment.
3. **Advanced** — Measure cache economics: instrument 20 golden questions; run with cold vs. warm retrieval cache and (if a real provider is wired) cold vs. warm provider prefix cache. Report latency and token-cost deltas, then compute the break-even corpus change frequency at which invalidation overhead exceeds caching benefit. That arithmetic is Chapter 31's methodology arriving one chapter early.

## Common failures

- **Key-collision leaks.** Caching per query, forgetting policy → cross-tenant serving. The most dangerous cache bug in this domain, and entirely deterministic to prevent.
- **Stale-by-design.** "Cache for 24 hours" with no corpus event hookup, on a corpus that changes hourly. Pick invalidation triggers from *how the data actually changes*, not round numbers.
- **Prefix-cache cargo-culting.** Assembling dynamic content first "for relevance" and never understanding why provider caching never helps. Order is a cache property.
- **Unbounded fragment growth.** Versioned fragments accumulating forever; retention rules apply to caches too (Chapter 26).

## Summary

- Four layers; you own fragments and retrieval caching, provider caching is a prefix property you *design for* but verify before relying.
- Cache keys encode governance: access policy and corpus version are key material; expiry is event-driven where you own ingestion.
- Caches inherit every correctness rule — isolation, staleness bounds, redaction — and their failures are silent, so their tests are mandatory.

## Mastery checklist

- [ ] I can write a leak-proof cache key and name each component's failure story.
- [ ] I can explain why KIND_GROUPED ordering is also the cache-friendly ordering.
- [ ] I can design event-driven invalidation for the corpus I own.

## Review questions

1. Why does a retrieval cache key include the access policy — what exactly leaks otherwise?
2. Why is "cache for 24 hours" usually the wrong invalidation policy for a versioned corpus?
3. What makes a request prefix cacheable, and what assembly decision controls it?

## References

- Provider prompt caching: consult the *current* documentation of your specific provider for mechanics, pricing, and limits (provider facts; re-verify before relying; reviewed 2026-10-20 as a claim class, not per-provider).
- Implementation pattern: content-addressed fragments tie into `assembly.py` ordering and `provenance.py` versioning.

## Next

Part IV: what the request *remembers* — conversation history, persistent memory, and task state.

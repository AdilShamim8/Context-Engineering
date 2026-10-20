# Chapter 9 — Provenance, Freshness, and Access-Aware Retrieval

> Part II · Knowledge Sources
> Prerequisites: Chapter 7 · Status: complete
> Time: ~75 minutes

## Overview

Everything in this chapter happens **before ranking matters and before any model runs**, and it is where retrieval stops being an information-retrieval problem and becomes an *authorization and correctness* problem. You will implement three policy families — access control (fail-closed), freshness, and version selection — all present in `provenance.py` and all pinned by tests. By the end you should be unable to look at a RAG demo without asking: "where is your access filter, and why is it after the ranker?"

## Provenance as the enabling substrate

Chapter 3 defined provenance; here it becomes load-bearing machinery. Every capability in this chapter requires it:

| Capability | Requires |
|---|---|
| Refuse when evidence is restricted | `access` class per source |
| Label or exclude stale evidence | `effective_date` per source |
| Stop superseded versions competing | `id` + `version` + `supersedes` |
| Cite answers correctly | full identity: id, version, date |
| Audit what influenced an answer | all of it, retained through the pipeline |

None of these can be bolted on after retrieval returns plain strings. This is the first place the curriculum's central rule bites: **structure early, or pay forever.** The chunk dataclass carries its `SourceRef` from ingestion (`corpus.py`) through indexing into selection and assembly — you can watch it happen in the integration tests.

## Access-aware retrieval: fail closed, filter first

Two design rules with security weight:

**1. Filter before ranking (not after).** The index's `predicate` mechanism runs during candidate selection (Chapter 7). Filtering after ranking leaks *shape*: unauthorized hits occupied top-k slots, displaced allowed results, and your returned "best allowed" answer is a function of forbidden scores. The tests pin the correct order: with an internal predicate, `restricted:hr-confidential` chunks are absent even from the candidate set of a compensation query.

**2. Fail closed on missing access metadata.** `_access_of` returns `ACCESS_UNKNOWN` for chunks with no access class, and `AccessPolicy.from_levels` does not include unknown → excluded. The alternative (default to allowed) means one malformed chunk silently becomes world-readable. Failing closed can *deny legitimate queries* — that is the correct trade in systems where the failure direction is asymmetric. The test suite demonstrates it explicitly: a chunk with no `SourceRef` is filtered out by a normal policy.

Two further consequences to internalize now (Part VI expands them): *user identity must enter the pipeline as a policy, not a string in the prompt* — the model is never consulted about authorization; and *tenancy is a special case of access* — the same predicate mechanism enforces per-tenant isolation (Chapter 25).

## Freshness: policy, not hope

`FreshnessPolicy` implements the three defensible postures toward age:

- **exclude** — stale sources drop from candidates entirely. Right for volatile operational data (status pages, pricing, schedules).
- **label** — stale sources stay, but the assembly adds a stale marker. Right for policy/history where the document is useful but must not silently win.
- **allow** — age irrelevant by domain. Say so explicitly rather than by omission.

The verdict object reports what it did and why ("no effective date on source; freshness unassessed"), because **a policy that cannot explain itself cannot be debugged** (Chapter 4's diagnostic loop demands reasons, not just booleans). Note the missing-date handling: unassessed ≠ fresh. The `data-retention-schedule` document (effective 2025-12-01) is the corpus's aging canary — the Chapter 9 lab uses it to watch each policy behave differently on the same query.

## Version selection: supersession as a mechanism

When retrieval serves "both versions, best wins," correctness rests on ranking luck. `select_current_versions` makes supersession a mechanism: newest numeric version per source id (effective date breaks ties) survives; superseded versions are dropped from candidates *before* ranking. The integration test demonstrates the payoff on the corpus's planted conflict: only `hr-remote-work v2` remains reachable as a candidate, so the "confident, citable, wrong" failure (Lab 00 scenario 3) becomes *structurally impossible* rather than merely unlikely.

Two honest notes. First, this policy (keep-and-archive in the corpus, filter-in-retrieval) is one of three defensible designs — Chapter 5 covered when point-in-time corpora beat it. Second, version metadata is a *social* contract: `select_current_versions` trusts the manifest the way a database trusts a primary key. If ingestion lets two "current" versions in, the mechanism faithfully serves whichever compares greater. Governance (Chapter 5) is upstream of this code, and its tests are therefore upstream of your confidence in it.

## Conflicting information: represent, don't resolve silently

Sometimes conflicts survive version selection: two *different* sources contradict (the vacation policy says carryover caps at 5 days; an older benefits FAQ says 3). Options when your pipeline detects disagreement (via `group_by_source` and disagreement detection): prefer the authoritative owner (needs the `owner` field — provenance again), include both with labels, or refuse and escalate. What is not acceptable is *silent* resolution — letting ranking flip a coin between sources the user cannot see disagree. The general principle: **conflict is information; it belongs in the context (labeled) or in an escalation, never in a coin flip.**

## Worked example: the full pre-model gauntlet

Assemble the pre-model stages every query runs before any model sees anything:

```python
from context_engineering.corpus import load_chunks
from context_engineering.provenance import (
    AccessPolicy, FreshnessPolicy, select_current_versions,
)
from context_engineering.retrieval import LexicalIndex

chunks = load_chunks("datasets/synthetic/corpus")

# Stage 1: version selection — superseded sources cannot compete
chunks = [c for c in chunks if f"-v{c.source.version}-" in c.chunk_id]  # (see note)
# Cleaner: select current versions at the document level, then reload chunks
# (the lab does exactly this — the naive one-liner above is the trap you'll fix)

# Stage 2: access filtering — fail closed, before ranking
policy = AccessPolicy.from_levels("public", "internal")

# Stage 3: freshness — label the aging canary
freshness = FreshnessPolicy(max_age_days=180, on_stale="label")

index = LexicalIndex(chunks)
hits = index.search(query, k=6, predicate=policy.as_predicate())
```

Note the deliberate trap in Stage 1: version selection must happen at the *document* level (before chunking), not on chunk ids — a string filter like the one above drops v1 chunks but is fragile, version-blind to non-numeric schemes, and teaches nothing about provenance. The Chapter 9 lab has you implement it correctly with `select_current_versions` on document sources, then retrieve, then run freshness verdicts on the *hits*, labeling stale evidence before assembly.

## Exercises

1. **Beginner** — Run `FreshnessPolicy(max_age_days=365, on_stale="exclude")` against every corpus document with today's date. Which documents drop? Which policy would make `data-retention-schedule` dangerous to *use* but safe to *cite*?
2. **Intermediate** — Implement `current_corpus_chunks(corpus_dir)`: load documents, `select_current_versions` over sources, load chunks only for current documents (extend `load_chunks` or filter its output by version). Verify: the remote-work query can no longer reach v1, ever.
3. **Advanced** — Implement tenant isolation: extend `AccessPolicy` with a tenant id in chunk metadata (`tenant: "acme"`), and write the test proving tenant A's query never sees tenant B's chunks — using only the predicate mechanism. Then write the one-paragraph incident report: what would happen if a teammate "optimized" the predicate to run after ranking?

## Common failures

- **Post-ranking filtering.** The recurring silent authorization bug; covered above — if you remember one thing from Part II, remember this.
- **Fail-open defaults.** "If access is missing, let's assume public" — one bad chunk becomes a leak. Fail closed, loudly.
- **Freshness by vibes.** "Documents are recent enough" without dates in metadata; the policy is only as real as the fields it reads.
- **Silent conflict resolution.** Ranking arbitrating between contradicting sources users cannot see.

## Summary

- Access control fails closed and filters *before* ranking; user identity enters as a policy object; tenancy is the same mechanism.
- Freshness is a three-posture policy (exclude/label/allow) whose verdicts explain themselves; missing dates mean unassessed, not fresh.
- Version selection makes supersession structural; conflicts that survive it must be labeled or escalated, never coin-flipped.

## Mastery checklist

- [ ] I can explain why filtering must precede ranking, including the k-truncation argument.
- [ ] I can implement current-version chunk loading and verify v1 is unreachable.
- [ ] I can run each freshness posture against a query and predict the difference.

## Review questions

1. What breaks when access filtering runs after ranking, beyond the obvious leak?
2. Why is "unassessed freshness" a different state from "fresh," and how should assembly render it?
3. When is keep-and-label better than drop-superseded, and what does each cost?

## References

- Implementation: `src/context_engineering/provenance.py`; tests `tests/unit/test_provenance.py`, `tests/integration/test_corpus_pipeline.py`.
- OWASP LLM Top 10 — access-control and sensitive-disclosure categories this mechanism exists to prevent — https://owasp.org/www-project-top-10-for-large-language-model-applications/ (reviewed 2026-10-20)

## Next

Part III: the assembled context as a first-class artifact — lifecycle, selection, budget, order, and compression.

# Chapter 5 — Designing a Reliable Knowledge Corpus

> Part II · Knowledge Sources
> Prerequisites: Part I · Status: complete
> Time: ~50 minutes

## Overview

Retrieval cannot be better than the corpus it draws from. Before any chunking, indexing, or ranking, someone decided *what goes in, who owns it, how fresh it must be, and who may read it*. This chapter teaches corpus design as a governance problem: source selection, authority, versioning, metadata, deduplication, and quality control — and applies it by walking the design of this repository's synthetic corpus (`datasets/synthetic/corpus/`), which every later lab uses.

## Why corpus design is a context-engineering concern

Chapter 4's failure taxonomy traced several failures to their upstream root: **missing information** (5. data problem) when the corpus never contained the answer, **stale evidence** when superseded versions are not marked, **contradiction** when both versions circulate freely, and **misleading content** when sources are wrong or adversarial. None of these are fixable downstream by cleverer ranking. A retrieval system over an ungoverned corpus is a machine for finding the wrong thing efficiently — and it will find it *confidently, with a citation*.

That is why this chapter's ideas are enforced in the curriculum's own corpus rather than described abstractly. The manifest (`manifest.json`) is the governance record, and every field exists because of a failure mode:

| Manifest field | Failure it prevents |
|---|---|
| `id`, `version` | Contradiction: both v1 and v2 treated as live answers |
| `effective_date` | Staleness: no way to tell 2024 policy from 2026 policy |
| `supersedes` / `superseded_by` | Version drift: no machine-readable pointer from old to new |
| `access` | Unauthorized disclosure: restricted docs flowing to any request |
| `owner` | Rot: nobody accountable when content ages or breaks |
| `synthetic_injection` flag | Accidental "live" injection fixtures outside the security lab |

## Source selection and authority

A corpus is a bet about which sources deserve the model's attention. The design questions:

1. **Authority.** Is this source the system of record for this topic? HR policy belongs to people-ops; deployment procedure belongs to platform reliability. Mixing a wiki *about* a policy with the policy itself invites the wiki to win ties it should never win.
2. **Coverage.** Which questions must the system answer, and does a source exist for each? The absence of a needed document is discovered either by corpus planning or by users, later, painfully.
3. **Intended audience.** Every document has readers it is *for* and readers it must never reach. Encode audience as an access class at ingestion, not at answer time (Chapter 9).
4. **Volatility.** Documents that change weekly (runbooks, status pages) need owners and update rhythms; stable ones (glossaries) do not. Volatility determines review cadence.

The Nimbus corpus deliberately includes three audience classes (`public`, `internal`, `restricted:<group>`) and both an HR-owned policy space and an engineering-owned operations space, so these decisions are visible rather than abstract.

## Versioning and supersession

The corpus keeps `hr-remote-work` **v1 and v2 on purpose**. Real corpora accumulate exactly this: the old file still exists somewhere, and naive retrieval happily serves it. Three policies are defensible:

- **Archive-and-flag** (used here): keep superseded versions, marked `superseded_by`, excluded from live retrieval via version selection (Chapter 9's `select_current_versions`). Best for auditability.
- **Delete-and-log**: remove the old version from the corpus entirely. Simple, but destroys the ability to answer "what did the policy say in March?".
- **Point-in-time corpora**: version the *whole corpus* (snapshots) so temporal questions query a snapshot. Expensive; correct for legal/compliance domains.

What is *not* defensible is the default: keeping both versions with no machine-readable relationship. That policy produced Lab 00 scenario 3.

## Deduplication and corpus hygiene

Duplicates inflate retrieval (the same policy returned three ways), confuse ranking (three near-identical chunks crowd out a better one), and waste budget. Hygiene checks worth automating: exact-duplicate detection by hash; near-duplicate detection by token overlap; orphaned files not in the manifest (the loader in `corpus.py` *refuses to load them* — silently ignoring an unlisted file hides corpus drift); and manifest entries with missing files (the loader raises — a corrupt corpus should be loud, Chapter 30).

## Worked example: auditing the Nimbus corpus

Run the integration tests (`python -m unittest tests.integration.test_corpus_pipeline`) and read `manifest.json` alongside them. Note what the tests pin down: every document has an effective date, owner, and access level; the superseded policy is detectable; the restricted documents are marked; the injection fixture exists in exactly one chunk and is flagged. A corpus with passing governance tests is *load-bearing* for every later stage — you can now trust failures to be interesting rather than foundational.

## Exercises

1. **Beginner** — Add a `public` document to the corpus (say, a fictional company glossary) with a complete manifest entry. Run the tests. What changes, and what should you add to the test suite?
2. **Intermediate** — Write a small script that loads the corpus and reports, per source id, how many versions exist and which is current (use `group_by_source` and `select_current_versions`). Identify every multi-version source.
3. **Advanced** — Design the manifest changes needed to support point-in-time queries ("what did the remote policy say on 2025-01-01?"), then argue for or against implementing it here versus keeping the archive-and-flag policy.

## Common failures

- **The wiki-shadowing problem.** An unofficial summary outranks the authoritative source because it repeats the query terms more often. Fix: authority in selection, not just ranking.
- **Metadata theater.** Manifest fields nobody maintains. Every field needs an owner and a test that reads it.
- **The "temporary" doc.** Drafts and scratch notes ingested "temporarily" become permanent, then authoritative-looking. Ingest only what has an owner.

## Summary

- Corpus quality bounds every downstream stage; governance failures surface later as confident, citable wrong answers.
- Every manifest field maps to a prevented failure — versioning, freshness, access, ownership.
- Supersession must be machine-readable; the loader must be strict (loud on drift, blind to nothing).

## Mastery checklist

- [ ] I can justify every field in `manifest.json` from memory via its failure mode.
- [ ] I can design (not just describe) versioning, access, and ownership for a small corpus.
- [ ] I can explain why the loader refusing unlisted files is a feature.

## Review questions

1. Why is "delete the old version" sometimes right, and what capability does it destroy?
2. Which Chapter 4 failures are corpus problems in disguise? Name at least three.
3. What makes a source authoritative, and where must that authority be enforced?

## References

- Implementation: `datasets/synthetic/corpus/manifest.json`, `src/context_engineering/corpus.py`, `tests/integration/test_corpus_pipeline.py`.
- Lewis et al., *RAG for Knowledge-Intensive NLP Tasks* — grounding knowledge needs a defined knowledge source — https://arxiv.org/abs/2005.11401 (reviewed 2026-10-20).

## Next

Chapter 6: turning documents into normalized, provenance-carrying records — ingestion.

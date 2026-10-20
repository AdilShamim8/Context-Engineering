# Roadmap and Build Status

This file tracks what exists, what is planned, and what comes next. The curriculum itself is specified in [`CURRICULUM.md`](CURRICULUM.md); this page records execution status and maintenance decisions.

## Current status (updated 2026-10-20)

| Area | Contents | Status |
|---|---|---|
| Part 0 — Orientation | Chapters 0.1–0.3, Lab 00 (first context experiment) | Complete |
| Part I — Foundations | Chapters 1–4, glossary, reference library | Complete |
| Part II — Knowledge & Retrieval | Chapters 5–9, synthetic corpus, chunking + retrieval + provenance code | Complete |
| Part III — Construction | Chapters 10–16, selection + compression + pipeline code | Complete |
| Part IV — Memory & State | Chapters 17–19, history + memory code | Complete |
| Part V — Tools & Agents | Chapters 20–23, tools + orchestrator code | Complete |
| Part VI — Security | Chapters 24–26, security code, security test lab | Complete |
| Part VII — Evaluation | Chapters 27–29, evaluation + observability code, golden suite | Complete |
| Part VIII — Production | Chapters 30–33, hardened pipeline | Complete |
| Part IX — Capstone | Chapters 34–39, knowledge assistant application, project portfolio | Complete |
| Projects | Beginner (2), intermediate (3), advanced (3), capstone (1+) | Complete |
| Labs | 7 guided labs with solutions | Complete |

## Deliberate scope decisions

1. **No license yet.** A license is a legal decision that belongs to the repository owner and is not added silently (see `docs/audit/2026-10-20-audit.md`). MIT or Apache-2.0 are common choices for educational code. Until resolved, others have no formal permission to reuse the content.
2. **Standard-library-first implementation.** All core teaching code runs on plain Python 3.10+ with zero third-party dependencies, so every chapter is reproducible offline. Optional adapters (exact tokenizers, embedding providers) are isolated behind interfaces.
3. **Deterministic-first.** Every concept that can be demonstrated without a model API is demonstrated without one. Model-dependent exercises exist but are clearly marked optional.
4. **Provider claims are dated.** Provider-specific capabilities (prompt caching, tokenizer specifics, API limits) change frequently; they are taught as concepts with a verify-before-rely note rather than frozen API claims.

## Suggested next iterations

Ordered by learning value; each is a self-contained contribution:

1. **Model-backed exercise pack** — an optional module wiring the deterministic responder's interface to a real provider behind the existing boundary, so the same labs can run against a live model.
2. **Semantic retrieval adapter** — implement the `EmbeddingProvider` interface with a local embedding model and rerun Part II labs to compare lexical vs. semantic retrieval on the same corpus.
3. **CI workflow** — run the test suite on push once the owner chooses a supported runner configuration.
4. **Deep-dive chapter expansions** — community-contributed worked examples per chapter (see `CONTRIBUTING.md`).
5. **License decision** — owner action item; unblocks broad reuse.

## Maintenance policy

- Content that makes a technical claim about a changing API carries a *reviewed* date. Claims older than six months should be re-verified before being relied on.
- The synthetic corpus is fictional. Never replace it with real documents or user data.
- Security reports follow `SECURITY.md`, not GitHub issues.

# Part II — Knowledge Sources, Ingestion, and Retrieval

> Chapters 5–9 · Prerequisites: Part I · Outcome: a governed corpus, ingested with provenance, retrievable with access control, freshness policy, and version awareness.

## Chapters

| # | Chapter | Focus |
|---|---|---|
| 5 | [Designing a Reliable Knowledge Corpus](chapter-05-corpus-design.md) | Governance: authority, versioning, metadata, ownership |
| 6 | [Document Ingestion and Normalization](chapter-06-ingestion.md) | Parse, extract, preserve structure, propagate provenance |
| 7 | [Chunking, Indexing, and Retrieval Fundamentals](chapter-07-chunking-and-retrieval.md) | Boundaries, BM25 from scratch, embeddings' place, hybrid fusion |
| 8 | [Advanced Retrieval and Search Planning](chapter-08-advanced-retrieval.md) | Rewrites, decomposition, reranking — and when *not* to |
| 9 | [Provenance, Freshness, and Access-Aware Retrieval](chapter-09-provenance-freshness-access.md) | Fail-closed access, freshness postures, version selection |

## What you build in this part

The synthetic Nimbus Dynamics corpus (`datasets/synthetic/corpus/`) is the part's living artifact: a governed, versioned, access-classified knowledge base with an honest conflict (two remote-work policy versions), an aging canary (`data-retention-schedule`), restricted documents that must never leak, and one flagged synthetic injection fixture for Part VI.

Code you can now read end-to-end: `chunking.py` (two strategies), `retrieval.py` (inverted index + BM25 + RRF fusion), `provenance.py` (access/freshness/version policies), `corpus.py` (strict loader). Every module ships with unit tests, and `tests/integration/test_corpus_pipeline.py` pins the governance behaviors the rest of the curriculum depends on.

## Completion criteria

- [ ] You can justify every manifest field by its failure mode (Ch. 5).
- [ ] You can ingest a new document version and let the tests catch your mistakes (Ch. 6).
- [ ] You can explain BM25's three ideas and implement a chunker change with predicted effects (Ch. 7).
- [ ] You can diagnose the four query-side retrieval failures and justify any extra stage (Ch. 8).
- [ ] You can prove — from tests — that restricted content is unreachable and superseded versions cannot win (Ch. 9).

Next part: [Part III — Dynamic Context Construction](../03-context-construction/).

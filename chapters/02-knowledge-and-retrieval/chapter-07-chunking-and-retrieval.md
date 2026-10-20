# Chapter 7 — Chunking, Indexing, and Retrieval Fundamentals

> Part II · Knowledge Sources
> Prerequisites: Chapter 6 · Status: complete
> Time: ~90 minutes

## Overview

This is the most implementation-dense chapter so far: you will understand chunk boundaries, size/overlap trade-offs, lexical ranking (BM25, implemented from scratch in `retrieval.py`), the role of embeddings and vector indexes, metadata filtering, and hybrid retrieval. Equally important is what the chapter argues *against*: that a vector database is a precondition for any RAG system. It is not, and the burden of proof is on complexity.

## Chunking: size, overlap, boundaries

A chunk is the unit of retrieval, so chunking policy determines the *resolution* of everything downstream. Three decisions:

**Size.** Larger chunks carry more context per hit (fewer "right chunk, missing sentence" failures) but dilute scores and crowd the budget. Smaller chunks retrieve precisely but fragment answers. The Nimbus loader uses ~160 words — big enough for a complete policy clause plus its heading, small enough that a handful fits any sane budget.

**Overlap.** Overlapping windows (10–20% typical) insure against the *boundary failure*: the answer sits at a chunk seam, half in each window, so no single chunk contains it. The cost is duplicated tokens and possible double-citations. `chunk_by_words` implements the window with overlap; `chunk_markdown` instead aligns boundaries to structure — see below.

**Boundaries.** This is the decision that matters most. Compare the two implementations side by side:

- `chunk_by_words`: sliding word window. Predictable, uniform, structure-blind — it will cut "…requests must be approved by the" | "manager." in half.
- `chunk_markdown`: heading/paragraph-aware. Section boundaries are semantic boundaries; the heading travels with its paragraphs.

Structure-aware wins whenever documents have structure (policies, runbooks, docs); flat windows win for uniform streams (logs, transcripts). Neither is universal, and Chapter 28 will make you *measure* the difference on the same corpus rather than argue about it.

## Lexical retrieval: what BM25 actually computes

`LexicalIndex` implements the classic pipeline: tokenize → inverted index → score. Read the ~80 lines; the ideas, in order:

1. **Document frequency.** A term appearing in every document cannot discriminate (idf → 0 in the limit). `math.log(1 + (N - df + 0.5)/(df + 0.5))` gives rare terms large positive weight.
2. **Term saturation.** A chunk saying "vacation" five times is more relevant than one saying it once — but not five times more. `k1` (default 1.5) controls how quickly additional occurrences stop helping.
3. **Length normalization.** A long chunk accumulates more term hits merely by being long. `b` (default 0.75) discounts raw term counts in long documents relative to the average length.

Then run the honest experiment the tests encode: `search("remote")` returns nothing — because the corpus says "remotely" and **lexical retrieval is exact-token matching**. No stemming is implemented, deliberately, so the gap is felt rather than narrated. Its real-world consequences: users phrase questions differently from documents ("PTO" vs "vacation"), which motivates Chapter 8's query rewriting and semantic retrieval.

## Do you need a vector database?

The honest engineering answer, which this corpus makes concrete: **at this scale, no, and pretending otherwise is complexity without evidence.** A vector database earns its place when (a) semantic matching beats lexical matching *for your queries* — paraphrase, synonym-heavy domains, cross-lingual; (b) the corpus is large enough that brute-force scoring (including semantic) is too slow; and (c) you have solved operational concerns that embeddings introduce: model versioning, re-embedding on corpus updates, dimension migrations, and cost.

BM25 remains a startlingly strong baseline — decades of information-retrieval tuning are baked into those three ideas above, and hybrid systems (lexical + semantic, fused via RRF) are the industry's robust default rather than a concession. This repository implements `rrf_fuse` so a semantic adapter (optional, behind an `EmbeddingProvider` boundary) can plug in and *compete* with lexical retrieval on the same eval suite, which is the only arbiter that matters (Chapter 27).

## Embeddings, conceptually

Semantic retrieval embeds text into a learned vector space where paraphrases land near each other. It fixes the exact-token gap ("PTO" ≈ "vacation") at the cost of: a model dependency, similarity that is *sometimes* wrong in ways lexical never is (near ≠ relevant — "remote work" sits near "remote control"), and the operational stack above. When you do adopt it: embed the *same normalized text* you index lexically; keep chunk ids stable so RRF fusion has something to fuse; and re-run the full eval suite, because semantic retrieval will *change which* failures you have, not eliminate them.

## Metadata filtering — and the security-shaped hole it fills

`LexicalIndex.search` takes a `predicate(chunk) -> bool` applied **before scoring**. This is not a convenience — it is where Chapter 9's access policy physically attaches. The integration tests pin the behavior: restricted chunks never even *rank* for unauthorized queries. Internalize the ordering: **filter first, rank second.** Ranking first and filtering after means unauthorized content has already influenced your top-k window — you then return the "best allowed" result shaped by forbidden scores, and with k-truncation you may have dropped allowed results to make room for filtered-out ones.

## Hybrid retrieval

When two retrievers disagree productively (lexical and semantic), fuse by rank, not by score. Reciprocal Rank Fusion (`rrf_fuse`) scores each item Σ 1/(60 + rank) across lists: robust, parameter-light, and immune to incomparable score scales (BM25's unbounded scores vs. cosine's bounded ones). The test suite demonstrates the key property: an item ranked high in *both* lists outranks an item ranked first in only one.

## Worked example: from question to ranked chunks

```python
from context_engineering.corpus import load_chunks
from context_engineering.retrieval import LexicalIndex
from context_engineering.provenance import AccessPolicy

chunks = load_chunks("datasets/synthetic/corpus")
index = LexicalIndex(chunks)
policy = AccessPolicy.from_levels("public", "internal")   # a normal employee

hits = index.search(
    "How many remote days per week are allowed?",
    k=5,
    predicate=policy.as_predicate(),   # restricted chunks excluded BEFORE ranking
)
for hit in hits:
    print(f"{hit.score:>8.4f}  {hit.chunk_id:28s} {hit.source.citation()}")
```

Note what the loop prints that naive RAG demos never show you: **the versioned citation**. When v1 and v2 both match, v2 outranks v1 for this corpus — but Chapter 9 will show why "outranks" is not a correctness mechanism, merely a hope. Retrieval returns candidates; *policy* decides which may serve.

## Exercises

1. **Beginner** — Change `load_chunks` max_words to 60, then 400; re-run the golden questions you know so far ("remote days", "vacation carryover"). Where does each extreme hurt?
2. **Intermediate** — Add stemming to a *copy* of `tokenize` (a crude suffix stripper: -s, -ing, -ly) and re-index. Does the "remote"/"remotely" gap close? What new collisions appear? Keep the results; you will use them in Chapter 27's ablation.
3. **Advanced** — Implement `KeywordBackedIndex`: a second retriever that expands the query with a tiny synonym table (PTO→vacation, onboarding→orientation), then fuse it with `LexicalIndex` via `rrf_fuse`. Evaluate on five hand-written questions where pure lexical fails.

## Common failures

- **Boundary-cut evidence** ("the chunk ends mid-sentence and the answer was in the cut part"). Structure-aware chunking or overlap; measure both.
- **Score-worship.** BM25 scores are not calibrated probabilities across queries; use them for ordering, not for "is 9.2 good?" decisions (Chapter 11 revisits).
- **Vector-database cargo-culting.** Adopting the stack before demonstrating a lexical-vs-semantic gap on your own eval suite.
- **Post-ranking filtering.** The silent security hole; filter before ranking, always.

## Summary

- Chunking is a resolution decision: size, overlap, and especially boundaries; structure-aware beats flat when structure exists.
- BM25 = idf × saturation × length normalization; strong baseline; exact-token (no stemming) — feel the gap, then close it deliberately.
- Vector databases earn complexity only when your eval suite demonstrates the gap; fuse retrievers by rank (RRF), filter by access *before* ranking.

## Mastery checklist

- [ ] I can explain every term in the BM25 formula and why each exists.
- [ ] I can implement or modify a chunker and *predict* which failures each change prevents or causes.
- [ ] I can argue for/against a vector DB for a given corpus with evidence-shaped reasoning.

## Review questions

1. Why does filtering before ranking differ from filtering after — give the k-truncation argument.
2. What failure does overlap insurance cause when overused?
3. Why is RRF safer than score-sum fusion for combining BM25 and cosine results?

## References

- Robertson & Zaragoza, *The Probabilistic Relevance Framework: BM25 and Beyond* — the ranking function implemented — (reviewed 2026-10-20)
- Lewis et al., *RAG* — the retrieval-grounding formulation — https://arxiv.org/abs/2005.11401 (reviewed 2026-10-20)
- Implementation: `src/context_engineering/{chunking,retrieval}.py`; tests `tests/unit/test_{chunking,retrieval}.py`, `tests/integration/test_corpus_pipeline.py`.

## Next

Chapter 8: query rewriting, decomposition, reranking — and the discipline of not adding stages.

# Chapter 8 — Advanced Retrieval and Search Planning

> Part II · Knowledge Sources
> Prerequisites: Chapter 7 · Status: complete
> Time: ~55 minutes

## Overview

Chapter 7 built a retriever; this chapter is about *querying it well* — and about the discipline that keeps retrieval from accreting stages. Query rewriting, decomposition, multi-step retrieval, and reranking each solve a real failure; each also adds latency, cost, and new failure modes. The chapter's core skill is a decision procedure: when a stage is justified by evidence, not by fashion.

## The query-side failure modes

Retrieval fails at the query at least as often as at the corpus. Four recurring shapes:

1. **Vocabulary mismatch.** The user says "PTO"; the policy says "vacation". Lexical search finds nothing, and the failure looks like "the system doesn't know" when it actually "didn't translate."
2. **Compound questions.** "Can I work remotely from another country and still get the commuting allowance?" is two policies wearing one sentence. A single query retrieves for whichever half has the stronger lexical match; the other half goes ungrounded.
3. **Underspecification.** "What about the policy?" — retrieval has no purchase. The system needs the conversational context to repair the query (Chapter 17) or must ask.
4. **Abstraction mismatch.** The user's question is at a different level than the documents ("is remote work flexible here?" vs. a policy with rules). Retrieval needs the query *concretized* into the vocabulary of the corpus.

## Query rewriting

Rewriting bridges the vocabulary gap *before* retrieval. Three workable, deterministic-friendly flavors:

- **Alias/synonym expansion.** A curated table (PTO→vacation, onboarding→orientation). Cheap, auditable, boring — and highly effective for closed-domain corpora where the term space is small. This is the Chapter 7 advanced exercise.
- **Query expansion by feedback (pseudo-relevance feedback).** Retrieve once, take terms from the top results, re-retrieve. Risk: if the first retrieval is wrong, expansion amplifies the wrong thing. Use only with an eval that can catch the drift.
- **Model-generated rewrites.** Rewrite "time off rules" → "vacation policy allowance" with an LLM. Strong for abstraction mismatch; costs a model call; **the rewrite inherits the model's hallucination risk**, so rewrites must never include asserted facts, only better *search vocabulary*.

## Query decomposition

For compound questions: split into atomic sub-questions, retrieve per sub-question, merge with `rrf_fuse`. Deterministic versions of decomposition are possible with pattern lists; production systems commonly let the model propose sub-questions (again: vocabulary only — never answers).

The critical design rule: **decomposition changes the context shape, not just the retrieval.** Two sub-questions mean two evidence groups; the assembler (Chapter 10's lifecycle) must label them ("Evidence for: commuting allowance…") or the model cannot tell which evidence answers which half.

## Multi-step retrieval (follow the citations)

Some evidence is one hop away: the retrieved chunk references "the deployment runbook, section 4" — the *referenced* document is what the answer needs. Multi-step retrieval iterates: retrieve, inspect references (links, section names, "see also"), retrieve again for the referenced artifact. Chapter 15's progressive disclosure is this idea generalized: retrieve *pointers* cheaply, expand *content* only when needed. Costs: extra round-trips, error compounding (a bad first hop poisons the second), and latency. Justify with evidence of one-hop failures in your eval transcripts (Chapter 29: the trace shows "answer referenced X; X never retrieved" — the multi-step signal).

## Reranking

First-stage retrieval (BM25, vector search) optimizes recall over large candidate sets cheaply; a reranker re-scores a small shortlist (top 20–100) with a stronger model — typically a cross-encoder in production, scoring (query, chunk) pairs jointly. BM25 sees "remote" matching "remote"; a cross-encoder sees "2 days per week" *answering* "how many remote days". The price: a model dependency and latency on every query.

Where a reranker fits in this repository: behind the same interface as any second-stage scorer, with the eval suite (Chapter 27) comparing `BM25-only` vs `BM25 + rerank` on identical golden cases. Until you have that comparison, reranking is a belief, not a decision.

## The anti-complexity discipline

Every stage added to retrieval must answer all four:

1. **Which measured failure does this fix?** (Name the transcript or eval case.)
2. **What does it cost per query?** (Latency, calls, tokens.)
3. **What new failure modes does it introduce?** (Amplification, drift, compounding, hallucinated rewrites.)
4. **How will we know if it made things worse?** (The regression suite that gates it.)

This is why the curriculum's baseline is deliberately plain: BM25 + access filtering + version selection. Every stage beyond it is an *experiment* you run against the harness, not a default you inherit from a framework's marketing page. Frameworks bundle all of these stages with attractive flags; Chapter 33 will compare them, but only after you can build and measure the baseline you would be handing them.

## Worked example: diagnosing a retrieval failure, then choosing the fix

Symptom: "What's the PTO carryover limit?" returns a benefits chunk, not `hr-vacation`'s carryover section. Dump the query the index actually saw: "PTO carryover limit". `hr-vacation` says "vacation days may carry over" — "PTO" never matches. The transcript shows failure shape #1 (vocabulary mismatch), so the evidence-backed fix is the cheapest one that closes it: an alias table mapping PTO→vacation (3 lines), then re-run the golden case. A reranker would *probably* also fix it — at 100× the complexity. Fix by failure shape, not by maximal machinery.

## Exercises

1. **Beginner** — Write the three-step diagnostic (dump query → classify failure shape → choose cheapest fix) as a checklist and apply it to "how do I get a new monitor?" on the Nimbus corpus.
2. **Intermediate** — Implement alias-table rewriting (PTO→vacation, laptop→equipment) as a `rewrite_query(query)` function; evaluate on five paraphrase questions before and after. Report which improved, which regressed (added terms can *dilute* matches — check).
3. **Advanced** — Implement two-step retrieval for the corpus: first pass retrieves; second pass takes each top-3 chunk's *section heading* as a new query, fuses with RRF. Measure on the eval suite: when does the second hop help, when does it drag in noise?

## Common failures

- **Stage accretion without evals.** Rewrite + rerank + multi-hop + filters added "for robustness"; nobody can attribute quality to any stage. Ablate (Chapter 28) or don't add it.
- **Hallucinated rewrites.** The model "helpfully" rewrites "carryover limit" → "carryover limit of 5 days" — inserting an *answer* into the query. Rewrite vocabulary only; forbid content.
- **Amplification loops.** Pseudo-relevance feedback on a bad first hit. Constrain expansion to term *types* (nouns from top chunk), cap the expansion size, and gate with evals.

## Summary

- Query-side failures: vocabulary mismatch, compound questions, underspecification, abstraction mismatch — each has a targeted, usually cheap fix.
- Rewrites change vocabulary, never facts; decomposition changes context shape (label sub-question evidence); rerankers score but must prove themselves on the eval suite.
- Every stage must name its failure, its cost, its new risks, and its regression gate.

## Mastery checklist

- [ ] I can classify a retrieval failure into its four query-side shapes from a transcript.
- [ ] I can implement alias rewriting and decomposition-fusion against the existing index.
- [ ] I can run the four-question justification for any proposed retrieval stage.

## Review questions

1. Why must query rewrites be restricted to vocabulary? What is the failure class otherwise?
2. Why does decomposition impose requirements on the *assembler*, not just the retriever?
3. What evidence justifies a reranker — and what evidence justifies *removing* one?

## References

- Gao et al., *HyDE* — the query-transformation family, including its risks — https://arxiv.org/abs/2212.10496 (reviewed 2026-10-20)
- Asai et al., *Self-RAG* — adaptive, on-demand retrieval decisions — https://arxiv.org/abs/2310.11511 (reviewed 2026-10-20)
- Carbonell & Goldstein, *MMR* — diversity at the selection stage — (reviewed 2026-10-20)

## Next

Chapter 9: the part of retrieval that outranks ranking — provenance, freshness, and access.

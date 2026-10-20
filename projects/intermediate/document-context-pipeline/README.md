# Project — Document Context Pipeline (Intermediate)

> Tier: Intermediate · Prerequisites: Part II (Chapters 5–7)
> Implementation: `src/context_engineering/{corpus,chunking}.py` · Tests: `tests/integration/test_corpus_pipeline.py`

## Objective

Build the ingestion half of a context system end-to-end: turn a governed document directory into retrieval-ready, provenance-carrying chunks — and prove the pipeline's integrity with tests rather than a demo screenshot.

## Scope and requirements

Your pipeline (extend the library, do not fork it) must:

1. **Load with strictness.** Read `manifest.json`; raise on manifest-listed files that are missing; refuse files not in the manifest.
2. **Chunk structure-aware.** Use `chunk_markdown` so headings travel with their paragraphs; keep word limits configurable.
3. **Carry provenance.** Every chunk holds its `SourceRef` (id, title, version, effective date, access, owner) plus metadata (ordinal, heading, fixture flags).
4. **Surface integrity statistics.** After loading, report: document count, chunk count, per-document chunk counts, largest/smallest chunk (words), and any documents producing zero chunks (a real failure: fully boilerplate or empty documents).
5. **Stay synthetic.** The Nimbus corpus only. Never wire real documents into this project.

## Deliverables

- Code (library extensions if needed) and a `pipeline_report()` function producing the statistics above.
- A test module extending the integration tests with at least: a zero-chunk document case (use a temporary in-memory fixture, not a corpus edit), an unlisted-file refusal case, and a manifest-missing-file exception case.
- A short written answer: which integrity checks protect *downstream* stages (retrieval, budgeting, citation) and how.

## Evaluation criteria

| Criterion | Pass standard |
|---|---|
| Strictness | All three failure cases raise; no silent skips |
| Provenance | No chunk missing source metadata (test-enforced) |
| Statistics | Report renders for the full corpus without error |
| Honesty | Limitations of structure-aware chunking stated in code docs |

## Definition of success

`python -m unittest discover` passes with your new tests included, and you can explain — from your own tests — why each strictness decision exists.

# Chapter 34 — First-Principles Reference Implementation

> Part IX · Integration and Capstone
> Prerequisites: Parts I–VI · Status: complete
> Time: ~60 minutes

## Overview

This chapter tours the `context_engineering` package as what it now is: a complete, working embodiment of every concept in the curriculum — a first-principles reference implementation you can read end to end in an afternoon, extend for the capstone projects, and carry as a mental model into any production stack you will ever touch. The tour maps concept → module → test, and names the deliberate design boundaries you would change (and keep) when porting the ideas to production infrastructure.

## The map

| Curriculum concept | Module | Pinning test |
|---|---|---|
| Approximate token estimation + honest limits | `tokens.py` | `test_tokens.py` |
| Component model: kinds, trust, provenance | `context.py` | `test_context.py` |
| Budget: priorities, truncation, reserved output, reports | `budget.py` | `test_budget.py` |
| Ordering + labeled assembly + trust delimiters | `assembly.py` | `test_assembly.py` |
| Deterministic responder (refusal policy) | `sim.py` | `test_sim.py` |
| Chunking: window + structure-aware | `chunking.py` | `test_chunking.py` |
| Lexical retrieval: BM25, filters, RRF | `retrieval.py` | `test_retrieval.py` |
| Access/freshness/version policy | `provenance.py` | `test_provenance.py` |
| Strict corpus loader | `corpus.py` | `test_corpus_pipeline.py` |
| Composite selection | `selection.py` | `test_selection.py` |
| Compression ladder rungs | `compression.py` | `test_compression.py` |
| Lifecycle stages: retries, fallbacks, degradation | `pipeline.py` | `test_pipeline.py`, `test_pipeline_hardening.py` |
| Bounded, audited history | `history.py` | `test_history.py` |
| Audited memory store | `memory.py` | `test_memory.py` |
| Guarded tool registry | `tools.py` | `test_tools.py` |
| Workflows + checkpoints + resume | `orchestrator.py` | `test_orchestrator.py` |
| Screening, wrapping, redaction | `security.py` | `test_security.py`, `test_security_pipeline.py` |
| Golden harness + ablations | `evaluation.py` | `test_evaluation.py`, `test_golden_suite.py` |
| Structure-not-content traces | `observability.py` | `test_observability.py` |
| The capstone request path | `apps/knowledge_assistant.py` | `test_knowledge_assistant.py` |

## Reading order for the tour (with what to notice)

1. **`context.py`** — the spine. Notice how small it is: kind, trust, priority, source. Everything else manipulates these objects; no module bypasses the model.
2. **`budget.py` + `selection.py`** — the decision pair. Notice both produce *reasons* (allocation records, selection metadata) — decisions without explanations don't exist here.
3. **`retrieval.py` + `provenance.py`** — the correctness pair. Notice the predicate parameter: authorization is an argument to search, not a filter after it.
4. **`security.py` + `assembly.py`** — the trust pair. Screening detects; wrapping delimits; neither *prevents* alone — Chapter 24's layered argument, in two files.
5. **`evaluation.py` + `observability.py`** — the evidence pair. Notice neither imports the assistant: the harness measures anything; the trace describes anything.
6. **`apps/knowledge_assistant.py`** — the assembly of it all. Read `answer_question` top to bottom: retrieve → screen → select → budget → assemble → respond, each stage traced, each decision inspectable. That function *is* Chapter 10's lifecycle, executable.

## Design boundaries you would change in production (honestly)

- **Retrieval**: BM25-in-memory is the teaching baseline; production swaps the index behind the same call shape (Ch. 33's port exercise) and adds semantic retrieval *with the ablation evidence to justify it*.
- **Persistence**: `CheckpointStore`, `MemoryStore`, history state are in-memory/dict-shaped by design; production gives them real storage — but the `to_state`/`from_state` boundaries are already the storage interface.
- **Responder**: the deterministic responder is a stand-in; production wires a model behind the *same* boundary and re-runs the model-dependent protocols (Ch. 28's rules). Nothing upstream changes — that is the entire point of the boundary.
- **Screening**: the heuristics are teaching-grade patterns; production heuristics evolve with the security lab's payload collection — but the policy hook (`enforce_no_high_severity`) and the layered-architecture posture stay.

## What to keep unchanged (the principles, not the code)

The component model. Filter-before-rank. Reasons with every decision. Fail-closed access. Trust labels in the request. Refusal as a first-class behavior. Traces of structure, never content. Golden cases as data, versioned with the corpus. One variable per ablation. These port to every stack — the code is their proof of work.

## Exercises

1. **Beginner** — Do the tour: read the six pairs above in order, and for each write one sentence about a decision the module made that you would have gotten wrong before this curriculum.
2. **Intermediate** — The portability drill: reimplement one module (start with `budget.py` — it's self-contained) in another language you know, *from its tests*, without reading the source. Where the tests force you to ask what the module does, the design succeeded; where they don't, tighten the test.
3. **Advanced** — Write the architecture brief for porting the whole stack to your production environment (named frameworks, named stores), naming per component: keep, replace, or extend — with the reason. This document is the strongest portfolio piece this curriculum produces.

## Mastery checklist

- [ ] I can name every module's job, its pinning tests, and its design partner.
- [ ] I can separate what to replace in production from what to keep, per module, with reasons.
- [ ] I can read `answer_question` and identify which chapter owns each line.

## Next

Chapter 35 builds the flagship on this foundation: the knowledge assistant you have already met via the CLI.

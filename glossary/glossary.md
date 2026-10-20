# Glossary

Terminology is used consistently with this glossary throughout the repository. When a term has competing industry definitions, the definition used here is stated explicitly.

**Access level** — An authorization class attached to a source (e.g., public, internal, restricted). Context assembly must filter by access level *before* content reaches a model context; prompt instructions are not an access-control mechanism.

**Ablation** — An experiment that removes or disables one context component at a time and measures the effect, to attribute quality to specific components. Implemented in `evaluation.py`.

**Assembly** — The stage that orders, labels, delimits, and serializes selected components into the final model request text. See `assembly.py`.

**BM25** — A probabilistic lexical ranking function (term frequency with saturation and length normalization). The reference retrieval implementation scores with BM25. See `retrieval.py`.

**Checkpoint** — A saved snapshot of task state enabling resumption after interruption with the minimum necessary information. See `orchestrator.py`.

**Chunk** — A retrievable unit of a document produced by chunking; carries a source reference and ordinal position.

**Chunking** — Splitting documents into retrieval-sized units with controlled size, overlap, and (ideally) structure awareness. See `chunking.py`.

**Citation** — An answer-level reference to the source(s) that grounded it; only possible when components carry provenance.

**Component kind** — The classification of a context element: instruction, user input, history, evidence, memory, tool definition, tool result, state, derived. See Chapter 3.

**Compression** — Any transformation that reduces token count while attempting to preserve task-critical information: deduplication, extractive selection, structured notes, summarization. Always potentially lossy; must be measured. See `compression.py`.

**Context** — The total information available to the model at one inference step: all components assembled into the request.

**Context budget** — The token capacity available for input components after reserving output space and safety margin. See `budget.py`.

**Context engineering** — The systematic design and management of the information available to a model at a particular inference or agent-execution step: selecting, retrieving, structuring, ordering, compressing, labeling, isolating, updating, and evaluating contextual information across an application's lifecycle.

**Context window** — The maximum token count a model accepts per request (input plus, in many APIs, reserved output). Provider-specific and changing over time; verify against current documentation.

**Derived representation** — A computed artifact standing in for raw content (summaries, transcripts, extracted tables, image descriptions). Trust and provenance inherit from the source.

**Deterministic demonstration** — An experiment whose outcome is fully reproducible without a model API; the mechanism being shown is mechanical (what fits, what got included), not model behavior.

**Effective working set** — The portion of the window actually occupied by high-value, current, relevant content — as opposed to framing, stale history, and noise.

**Embedding** — A learned dense vector representation of text enabling semantic similarity comparison. Conceptually covered in Chapter 7; optional adapters only, in this library.

**Evidence** — Retrieved content offered as grounding for an answer. Untrusted by default.

**Freshness policy** — Rules deciding whether a source's age makes it unusable or suspect (maximum age, hard fail, label-if-stale). See `provenance.py`.

**Golden case** — An evaluation fixture pairing an input with required facts, expected sources, and forbidden content. See `evaluation.py`.

**Hallucination** — Confident output not grounded in the provided context; typically the model's plausible completion when evidence is missing or ambiguous. A context-quality symptom before it is a model defect.

**History** — Prior conversation turns selected or summarized for the current request. See `history.py`.

**Hybrid retrieval** — Combining lexical and semantic signals (e.g., via reciprocal rank fusion) for more robust ranking.

**Inverted index** — The word→documents mapping underlying lexical search; implemented from scratch in `retrieval.py`.

**Lost in the Middle** — The empirical finding (Liu et al., 2023) that long-context performance often degrades when key information sits mid-context, approximating a U-shaped positional effect. Magnitudes vary; measure on your own model/task.

**Memory** — Information retained across interactions beyond raw history: facts, preferences, episodic notes. Auditable, expirable, deletable. See `memory.py`.

**MMR (Maximal Marginal Relevance)** — A selection method balancing relevance against redundancy/diversity.

**Provenance** — The metadata identifying a piece of content's origin: source id, title, version, effective date, access level, owner. Enables citations, freshness, access control, audit.

**Progressive disclosure** — Supplying lightweight references first and retrieving full content on demand, trading latency/calls for a smaller, more relevant context.

**Prompt engineering** — Designing instructions, examples, constraints, and output expectations. One component of context; taught in the companion `Prompt-Engineering` repository.

**Prompt injection** — Untrusted content that attempts to change model behavior (direct: from the user; indirect: embedded in retrieved/tool content). Contained by layered architecture, not by prompt wording. See Chapter 24.

**Provider caching / prompt caching** — Provider-side reuse of previously processed request prefixes, reducing latency/cost for repeated static prefixes. Mechanisms and pricing are provider-specific and time-sensitive: verify before relying.

**Reciprocal Rank Fusion (RRF)** — Robust method to merge multiple ranked lists: each item scores Σ 1/(k + rank), k typically 60.

**Redaction** — Removing or masking sensitive content (emails, tokens, identifiers) from logs and traces before storage. See `security.py`.

**Reserved output budget** — Window tokens set aside for the model's response; a missing reservation is the classic cause of mid-generation cutoffs.

**Reranking** — A second-stage scorer (often a cross-encoder model in industry) refining first-stage retrieval. Concept in Chapter 8.

**RAG (Retrieval-Augmented Generation)** — Retrieving external evidence to ground responses. One context source and one lifecycle consumer, not the whole discipline.

**Selection** — Choosing which candidate components enter the context: relevance, recency, authority, diversity, budget. See `selection.py`.

**State (task state)** — Structured application information about task progress, distinct from memory (durable user knowledge) and history (conversation transcript).

**Stale evidence** — A superseded or outdated source presented as current; produces confident, citable, wrong answers. Prevented by provenance + freshness policy.

**Summarization (rolling)** — Compressing dropped history turns into a running note retained in context.

**Tool definition / tool result** — The schema describing a callable tool / the output of calling it. Definitions are trusted app content; results are untrusted external content.

**Trace** — A per-stage record of what a pipeline did: timings, token counts, inclusions, drops, findings. The raw material of debugging and observability. See `observability.py`.

**Trust boundary** — The line between content your application authored and content that entered from outside. Trusted instructions and untrusted data are rendered differently and never merged as equals.

**Truncation** — Cutting component content to fit budget; a policy decision (what to keep, how to mark the cut), never a silent default.

**Version (of a source)** — The iteration identity of a document; enables supersession (v2 replaces v1) and conflict resolution. See `provenance.py`.

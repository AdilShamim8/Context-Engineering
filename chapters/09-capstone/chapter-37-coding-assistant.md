# Chapter 37 — Repository-Aware Coding Assistant

> Part IX · Integration and Capstone · *Optional on first pass*
> Prerequisites: Chapter 35 · Status: complete
> Time: ~60 minutes

## Overview

The same discipline, transplanted to the domain where context engineering arguably matters most commercially: helping a model work on a *codebase*. A repository is a corpus with unusual properties — executable, versioned, densely cross-referenced, and hostile to naive chunking — and this chapter walks the design: repository maps over raw dumps, task-scoped retrieval, tool-and-verification loops, and why coding agents fail when treated as "RAG over code." The chapter is design-first: you specify and prototype against this repository itself, which conveniently is the best fixture you have.

## Why code defeats naive context strategies

- **Size.** Repositories exceed every window; "include everything" was never an option here, which is why coding assistants were doing context engineering before it had a name.
- **Chunking granularity is structural, not statistical.** Splitting mid-function destroys the unit of meaning; the retrieval unit must be AST-aware (function, class, module) — the strongest argument in the whole curriculum for structure-aware chunking (Ch. 7).
- **Cross-references are semantic glue.** A question about `allocate()` needs `ContextBudget`'s definition, `TRUNCATABLE_KINDS`, and the tests that pin them. Flat lexical retrieval finds *mentions*; a coding assistant needs the *referenced* units — multi-hop by nature (Ch. 8/15).
- **The ground truth is executable.** Unique among corpora: you can *run* the answer's validity. Tests, imports, and type checks make coding the domain where Chapter 28's evidence loops close fastest — the verification loop is mechanical.

## The repository map: the pointer layer

The coding-assistant pattern with the best effort-to-value ratio: a **repo map** — one-to-three-line summaries per module (name, public functions, one-line purpose) — always in context (a few thousand tokens for a moderate repo), with full source behind a `read_file(path, lines)` tool. This is Chapter 15's progressive disclosure, instantiated: pointers first, content on demand, authorization per call. The map is Chapter 14's structured notes applied to architecture. What the map buys: the model can *plan* (which files, which order) before fetching anything; what it costs: map freshness (regenerate on merge; the corpus-version pattern, again) and map quality (a misleading one-line summary misdirects every plan that reads it — the summary is a derived representation with provenance, Ch. 23).

## Task-scoped retrieval: the query is the task

Coding questions arrive as *tasks* ("make `allocate` fail when output reservation is negative"), not queries. The retrieval shape that works: **decompose the task into its touch-points** (the function, its tests, its callers, its docs — Chapter 8's decomposition, domain-specialized), retrieve per touch-point, and let selection prefer *executable context* (the tests that will judge the answer) over prose. The curriculum's own tests are the fixture to prototype on: a question about budget behavior should retrieve `budget.py` *and* `test_budget.py` — because the answer's validity lives where its assertions are.

## The verification loop: tools close the cycle

The loop that separates coding agents from coding chat: edit → run tests → read failures → repair (Ch. 21's workflow, with the execution environment as the observer). Tool-context requirements, from Chapter 20: the runner tool's description teaches selection and bounds (`run_tests(module, pattern)` with output caps — test suites are chatty tool results); write tools are gated (the caller's permission set); and **failure output is context worth crafting** — the compilation error that enters context after a bad edit is the highest-signal component the loop will see all day. Chapter 30's ladder applies to a loop stage: a failing test run is not a pipeline failure; it is the observation the next iteration consumes. What must never degrade: the *timeout* and the *side-effect bounds* — the verification loop that can run arbitrary commands is Chapter 20's excessive-agency scenario wearing an IDE costume.

## Worked example: spec the assistant for *this* repository

Take the capstone's request path and re-instantiate per stage: corpus = this repo (loader: `Path.rglob` + AST-ish module summaries; chunking: module/class level); repo map = the development-guide's module table (already written, you'll notice, as a pointer layer); retrieval = lexical over code tokens (noting Ch. 7's exact-token gap hits code hard: `allocate` vs `allocates` — stemming matters here); touch-point decomposition = function name + `_test_` prefix lookup; tools = `read_file`, `run_tests`, each with descriptions, caps, and permissions; verification = `python -m unittest discover` as the oracle; eval = golden cases phrased as tasks ("Which module enforces the trust boundary at assembly?") with required facts pointing at `assembly.py`/`security.py`. Then the honest gap list: no real coding assistant ships without a model; the deterministic responder can't write code — this domain's *optional* model exercises are where the curriculum's boundary earns its keep.

## Exercises

1. **Beginner** — Write the repo-map entries for five modules of this repository (three lines each, Ch. 23's provenance format). Test: can you answer "where does access filtering happen?" from the map alone, without reading code?
2. **Intermediate** — Implement `read_file(path, lines)` and `run_tests(pattern)` as `ToolSpec`s with the full Chapter 20 discipline (descriptions, schemas, caps, permissions, error results). Script one verification loop against a deliberately broken test.
3. **Advanced** — Build the task-scoped retrieval prototype: given a task touching `budget.py`, assemble its touch-point context (module + tests + callers via grep) and measure: golden tasks answered from flat retrieval vs. task-scoped retrieval. Report where task-scoping won and where it dragged in noise.

## Mastery checklist

- [ ] I can justify every design delta between document QA and code QA (chunking unit, map layer, executable oracle) from earlier chapters by number.
- [ ] I can spec the five tool-context requirements for a verification loop and name the two that must never degrade.
- [ ] I can prototype repo-map + touch-point retrieval against this repository and evaluate it with golden tasks.

## Next

Chapter 38: the evaluation project — turning this curriculum's harness loose on variant comparison at full strength.

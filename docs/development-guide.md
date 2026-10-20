# Development Guide

For learners extending the library and for contributors. The curriculum itself lives in `chapters/`; this page covers how the code is organized, tested, and extended.

## The library at a glance

All core modules live in `src/context_engineering/` and import **only** from the Python standard library. That constraint is deliberate: it keeps every chapter reproducible offline and makes the whole library readable in a sitting or two.

| Module | Teaches | Introduced in |
|---|---|---|
| `tokens.py` | Approximate token estimation and its honest limits | Chapter 2 |
| `context.py` | The component model: kinds, trust levels, sources | Chapter 3 |
| `budget.py` | Priority-based allocation, truncation, reserved output | Chapter 12 |
| `assembly.py` | Ordering strategies and labeled rendering | Chapters 13, 24 |
| `sim.py` | Deterministic responder for reproducible experiments | Chapter 0.3 |
| `chunking.py` | Word-window and structure-aware chunking | Chapter 7 |
| `retrieval.py` | Inverted index, BM25 scoring, metadata filters, RRF fusion | Chapter 7 |
| `provenance.py` | Access filtering, freshness, version selection | Chapter 9 |
| `selection.py` | Recency/authority weighting, dedup, diversity | Chapter 11 |
| `compression.py` | Deduplication, extractive compression, structured notes | Chapter 14 |
| `history.py` | Bounded conversation history with pinned constraints | Chapter 17 |
| `memory.py` | Memory store: conflicts, TTL, deletion, audit | Chapter 18 |
| `tools.py` | Tool registry with permissions and schema checks | Chapter 20 |
| `orchestrator.py` | Multi-stage workflows with checkpoints and resume | Chapter 21 |
| `security.py` | Trust labels, injection screening, redaction | Chapter 24 |
| `evaluation.py` | Golden cases, coverage metrics, ablations, reports | Chapter 27 |
| `observability.py` | Stage traces with timings and redaction | Chapter 29 |
| `pipeline.py` | Stage composition with retries and fallbacks | Chapter 30 |
| `corpus.py` | Loader for the synthetic Nimbus Dynamics corpus | Chapter 35 |
| `apps/knowledge_assistant.py` | The capstone assistant tying everything together | Chapter 35 |
| `cli.py` | `budget` / `inspect` / `ask` / `evaluate` commands | Projects |

## Running and testing

```bash
# Full suite (zero dependencies)
python -m unittest discover

# Verbose single-module tests while developing
python -m unittest tests.unit.test_budget -v

# CLI smoke tests
python -m context_engineering.cli --help
python -m context_engineering.cli evaluate
```

Tests live in `tests/unit/` (per-module), `tests/integration/` (cross-module flows), and `tests/evaluation/` (golden-suite execution). `tests/__init__.py` puts `src/` on `sys.path`, so tests run without installing the package.

### Testing conventions

- Deterministic components get deterministic tests — no network, no randomness without a fixed seed, no sleeps.
- A test that documents a *limitation* (e.g., "heuristic estimation cannot be exact") asserts stable, documented bounds rather than exact wrongness.
- New modules ship with a `tests/unit/test_<module>.py` in the same commit. If a test is skipped, the skip reason names the optional dependency.

## Extending the library

### Adding a module

1. Create `src/context_engineering/<name>.py` with a module docstring stating: what it teaches, its scope, and what it deliberately does **not** do.
2. Dataclasses for inputs/outputs; pure functions for logic; no hidden global state.
3. Add `tests/unit/test_<name>.py`; wire the module into `cli.py` only if a project needs it.
4. Update the table above and the relevant chapter's *Implementation* section.

### Adding an optional adapter

Optional integrations (exact tokenizers, embedding models) follow a strict pattern:

```python
def make_estimator(exact: bool = False):
    """Return approximate heuristic estimator; upgrade to a real tokenizer
    only when the optional dependency is importable."""
```

Core code paths must import adapters lazily and degrade gracefully when absent. A chapter may *suggest* an adapter; it may never *require* one.

### Changing corpus data

The Nimbus Dynamics corpus (`datasets/synthetic/corpus/`) is governed by `manifest.json`. If you add or edit documents:

- Update `manifest.json` (id, file, title, version, effective date, access level, owner).
- Keep everything fictional. No real names, no real credentials, no real policy text.
- If a document intentionally contains a synthetic injection fixture, the manifest entry must say so (`"synthetic_injection": true`).
- Run `python -m unittest discover` — integration tests read the corpus and will catch inconsistency.

## Code style

- Python 3.10+; type hints on public functions; docstrings on every public module/class explaining the *teaching purpose*, not just mechanics.
- Prefer explicit over clever: a learner should follow the code without standard-library archaeology.
- Every module's docstring includes a **Limitations** section. Honest limitation statements are a feature of this repository, not a disclaimer.

## Commit and review discipline

One coherent change per commit; tests must pass before committing; commit messages follow the prefixes in `CONTRIBUTING.md`. Before pushing, verify nothing sensitive is staged:

```bash
git diff --cached | grep -E "ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|api[_-]?key\s*=" && echo "LEAK — do not commit" || echo "clean"
```

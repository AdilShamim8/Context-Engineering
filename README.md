# Context Engineering

A structured, end-to-end learning environment for **Context Engineering** — the discipline of deciding *what information a model sees at inference time*, obtaining it, assembling it safely, observing the result, and improving the system with evidence.

Context Engineering is more than prompt writing. Prompts are one component of context. This repository teaches the whole picture: instructions, conversation history, retrieved evidence, memory, tool definitions, tool results, application state — and the engineering of selection, budgeting, ordering, compression, trust, and evaluation that turns those components into a working system.

## What this repository contains

- **A curriculum** — 39 chapters in 10 parts, from orientation to capstone ([`CURRICULUM.md`](CURRICULUM.md)).
- **Detailed chapter notes** — concepts, diagrams, worked examples, exercises, mastery checklists (`chapters/`).
- **A reference library** — a first-principles, standard-library-only Python implementation of core components: token estimation, context assembly, budgeting, chunking, retrieval, memory, security screening, evaluation (`src/context_engineering/`).
- **Hands-on labs** — 7 guided labs with solutions (`labs/`).
- **A project portfolio** — 9 projects from beginner to capstone, all runnable locally without paid APIs (`projects/`).
- **A synthetic dataset** — the fictional *Nimbus Dynamics* corporate knowledge base, which evolves across the entire curriculum (`datasets/synthetic/`).
- **A test suite** — unit, integration, and evaluation tests, all deterministic (`tests/`).

## Quick start

```bash
git clone https://github.com/AdilShamim8/Context-Engineering.git
cd Context-Engineering

# Run the full test suite (no dependencies needed; Python 3.10+)
python -m unittest discover

# Make the library importable (pick one):
pip install -e .                       # recommended: enables the CLI everywhere
export PYTHONPATH=src                  # or run everything with PYTHONPATH=src

# Explore how a component bundle allocates under budget pressure
python -m context_engineering.cli budget

# Inspect exactly what context gets assembled for a question
python -m context_engineering.cli inspect

# Ask the capstone assistant a question (fully offline)
python -m context_engineering.cli ask "How many remote days per week are allowed?"

# Run the evaluation suite
python -m context_engineering.cli evaluate
```

Full setup instructions, including troubleshooting: `docs/getting-started.md`.

## Curriculum map

| Part | Theme | Chapters |
|---|---|---|
| 0 | Orientation, prerequisites, environment | 0.1–0.3 |
| I | Foundations: the discipline, tokens, anatomy of context, diagnosis | 1–4 |
| II | Knowledge sources, ingestion, chunking, retrieval, provenance | 5–9 |
| III | Lifecycle, selection, budgeting, ordering, compression, caching | 10–16 |
| IV | Conversation history, persistent memory, state | 17–19 |
| V | Tools, multi-step agents, multi-agent isolation, multimodal | 20–23 |
| VI | Prompt injection, privacy, governance | 24–26 |
| VII | Evaluation, test-driven practice, observability | 27–29 |
| VIII | Reliability, performance, deployment, comparisons | 30–33 |
| IX | Reference implementation and capstone projects | 34–39 |

Details, prerequisites, and completion criteria: [`CURRICULUM.md`](CURRICULUM.md). Build status: [`ROADMAP.md`](ROADMAP.md).

## Repository structure

```text
Context-Engineering/
├── README.md              ← you are here
├── CURRICULUM.md          ← full curriculum specification
├── ROADMAP.md             ← status and maintenance decisions
├── CONTRIBUTING.md         ← how to contribute
├── SECURITY.md            ← security policy
├── docs/                  ← getting started, prerequisites, guides, audit
├── chapters/              ← chapter notes, organized by part
├── labs/                  ← guided labs with solutions
├── projects/              ← portfolio projects (beginner → capstone)
├── src/context_engineering/ ← the reference library
├── tests/                 ← unit, integration, and evaluation tests
├── datasets/synthetic/    ← the Nimbus Dynamics corpus (fictional)
├── glossary/              ← terminology
├── references/            ← curated sources with review dates
└── scripts/               ← maintenance helpers
```

## Companion repositories

This repository is part of a learning ecosystem. Scope boundaries are deliberate:

- **Prompt writing** (instructions, examples, prompt patterns) → [`Prompt-Engineering`](https://github.com/AdilShamim8/Prompt-Engineering)
- **The overall GenAI engineering journey** (12-rung ladder, RAG, agents, evals, production) → [`GenAI-Roadmap-with-Notes-and-Projects`](https://github.com/AdilShamim8/GenAI-Roadmap-with-Notes-and-Projects)
- **Context Engineering in depth** (this repository) → construction, management, evaluation, security, and operation of context-aware systems.

## Intended audience

Engineers and technical learners who want to move beyond prompt tricks and build reliable, inspectable, evaluated context systems. Minimum background: comfortable Python, JSON, and basic HTTP/API ideas — see `docs/prerequisites.md` for a self-assessment checklist.

## Contributing, security, and license

- Contributions: [`CONTRIBUTING.md`](CONTRIBUTING.md)
- Reporting security issues: [`SECURITY.md`](SECURITY.md)
- **License: not yet chosen.** No license file exists; choosing one is an owner decision (see `docs/audit/2026-10-20-audit.md`). Until then, default copyright applies.

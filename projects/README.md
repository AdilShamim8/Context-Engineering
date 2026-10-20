# Project Portfolio

Nine projects, ordered by difficulty, each with an objective, architecture, requirements, deliverables, and evaluation criteria. All run offline on the synthetic corpus. Projects are *where the curriculum pays off*: every chapter's ideas converge into an artifact you can explain and defend.

## Difficulty tiers

| Tier | Projects | Prerequisites |
|---|---|---|
| Beginner | [Context Budget Explorer](beginner/context-budget-explorer/README.md) · [Context Inspector](beginner/context-inspector/README.md) | Parts I–III |
| Intermediate | [Document Context Pipeline](intermediate/document-context-pipeline/README.md) · [Retrieval & Assembly Engine](intermediate/retrieval-assembly-engine/README.md) · [Conversation & Memory Manager](intermediate/conversation-memory-manager/README.md) | Parts II–IV |
| Advanced | [Evidence & Source Manager](advanced/evidence-source-manager/README.md) · [Security Test Laboratory](advanced/security-test-lab/README.md) · [Context Evaluation Harness](advanced/context-evaluation-harness/README.md) · [Multi-Step Context Orchestrator](advanced/multi-step-orchestrator/README.md) | Parts V–VIII |
| Capstone | [Context-Aware Knowledge Assistant](capstone/knowledge-assistant/README.md) | All parts |

## How to work through a project

1. Read the spec's **Objective** and **Definition of success** first.
2. Implement against the library (`src/context_engineering/`) rather than reinventing — extending it is encouraged and often required.
3. Keep the eval habit: every project ends with evidence, not a demo. Run (or extend) the relevant test modules and record results.
4. Compare your work to the reference behavior in the test suite, where applicable — tests *are* the grading rubric for deterministic behavior.

## Implementation map

Projects map to library code so specs stay short:

- Budget Explorer → `budget.py` + CLI `budget`
- Context Inspector → `assembly.py` + CLI `inspect`
- Document Context Pipeline → `corpus.py`, `chunking.py`
- Retrieval & Assembly Engine → `retrieval.py`, `provenance.py`, `selection.py`, `assembly.py`
- Conversation & Memory Manager → `history.py`, `memory.py`
- Evidence & Source Manager → `provenance.py` (versioning, freshness, conflicts, access)
- Security Test Laboratory → `security.py` + synthetic fixtures
- Context Evaluation Harness → `evaluation.py`, `observability.py`
- Multi-Step Orchestrator → `orchestrator.py`, `tools.py`
- Capstone Assistant → `apps/knowledge_assistant.py` + CLI `ask`

## Portfolio expectations

If you complete all nine, your portfolio demonstrates: budgeting and allocation under pressure, inspectable assembly, governed retrieval, stateful memory, source lifecycle management, adversarial security testing with measured controls, evidence-based evaluation with ablations, multi-stage orchestration with checkpoints — and one integrated system that does all of it coherently. That is the CV answer to "what does a context engineer actually build?"

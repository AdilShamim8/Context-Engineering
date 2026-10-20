# Part VI — Security, Privacy, and Governance

> Chapters 24–26 · Prerequisites: Parts II–V · Outcome: a system that keeps adversarial content contained, private data scoped, and its own past answerable.

## Chapters

| # | Chapter | Focus | Code |
|---|---|---|---|
| 24 | [Prompt Injection and Untrusted Context](chapter-24-prompt-injection.md) | Threat model, layered defense, the attack lab | `security.py` |
| 25 | [Privacy, Multi-Tenancy, and Sensitive Information](chapter-25-privacy.md) | Minimization, three-door isolation, deletion boundaries | `provenance.py`, `memory.py` |
| 26 | [Provenance, Governance, and Lifecycle Management](chapter-26-governance.md) | Answerable-later questions, retention, change management | everything |

## The part's single idea

**Instructions are advice; architecture is security.** Every protection this part teaches is a property of the pipeline — access filtering before ranking, per-call tool permissions, wrapped untrusted content, keyed caches, audited memory, redacted traces, versioned corpus — and each one is testable code with its failure mode known. When your synthetic payload defeats the heuristics and the system is still safe, the architecture was right.

## Completion criteria

- [ ] You can name the seven layers and prove, from tests, which one holds any given attack (Ch. 24).
- [ ] You can enforce tenant isolation at all three doors and design cache keys that can't collide (Ch. 25).
- [ ] You can reconstruct a past answer's decision chain from artifacts, with no content stored (Ch. 26).

Next part: [Part VII — Evaluation, Testing, and Observability](../07-evaluation-and-observability/).

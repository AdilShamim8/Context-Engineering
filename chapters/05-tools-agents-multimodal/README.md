# Part V — Tools, Agents, and Multimodal Context

> Chapters 20–23 · Prerequisites: Parts III–IV · Outcome: the loop beyond one request — tools with permissioned hands, workflows with drift-proof resume, delegation with honest labels, and modality decisions made per artifact.

## Chapters

| # | Chapter | Focus | Code |
|---|---|---|---|
| 20 | [Tool Context and External Interactions](chapter-20-tool-context.md) | Selection-teaching descriptions, guarded execution, bounded outputs | `tools.py` |
| 21 | [Context Across Multi-Step Workflows](chapter-21-multi-step-workflows.md) | Per-stage context, state handoff, checkpoints, observation extraction | `orchestrator.py` |
| 22 | [Multi-Agent Context Isolation and Delegation](chapter-22-multi-agent.md) | When to split; delegation summaries as semi-trusted artifacts | patterns |
| 23 | [Multimodal Context Engineering](chapter-23-multimodal.md) | Raw vs. derived; alignment; budget per artifact | patterns |

## The part's single idea

Beyond one request, the context question recurs *per step, per agent, per artifact* — and the answer is always the same shape: **structure over accretion**. Tools get schemas and permissions instead of strings; workflows get state instead of transcripts; agents get delegation summaries instead of shared windows; modalities get derived representations instead of raw dumps. Every one of those is Chapter 10's lifecycle, specialized.

## Completion criteria

- [ ] You can ship a tool whose five failure paths all return structured, instructive results (Ch. 20).
- [ ] You can prove, from a trace, that interrupt → corpus change → resume picked up the new version (Ch. 21).
- [ ] You can write the four-justification memo for/against a multi-agent split and cost the merge step (Ch. 22).
- [ ] You can design a derivation chain whose provenance survives assembly into context (Ch. 23).

Next part: [Part VI — Security, Privacy, and Governance](../06-security-and-governance/).

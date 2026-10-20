# Chapter 22 — Multi-Agent Context Isolation and Delegation

> Part V · Tools, Agents, and Multimodal Context
> Prerequisites: Chapter 21 · Status: complete
> Time: ~45 minutes

## Overview

A multi-agent system is a workflow whose stages happen to be language models — plus one new engineering problem: **whose context sees what.** This chapter covers shared vs. private context, delegation summaries (the handoff artifact between agents), provenance of agent-produced claims, conflicting agent results, and the decision itself: *when is multi-agent worth it?* The honest position up front: most multi-agent complexity in the wild is fashion; the burden of proof sits with the architecture, and this chapter arms the prosecutor.

## When multi-agent earns its complexity

Splitting one model loop into several is justified by exactly four needs — everything else is resume-building:

1. **Context isolation as a security control.** A summarizer that never sees raw sensitive documents, a coder that never sees user PII — separate agents with separate access policies are a *coarse, enforceable* boundary. This is the strongest justification: isolation by architecture, not by instruction (Chapter 24's rule).
2. **Parallelism over genuinely independent subtasks.** Map-style work (analyze 20 files) parallelizes; but note the *merge* step then becomes the hard context problem (below).
3. **Attention for one thing at a time.** Long, multi-constraint tasks can behave better when one agent holds only one constraint set — the model attends within its window, not despite it. (Empirically variable; measure before believing — Chapter 27.)
4. **Different tool access per role.** The planner has read-only tools; the executor has write tools, gated by permission per Chapter 20. Role = tool set = blast radius.

The non-justifications to name out loud: "agents are the future" (not a requirement), "the framework demo looked good" (demos optimize for demos), "our task is complex" (complexity argues *against* — more moving parts, more failure surface; Chapter 30 multiplies per agent). The professional default: **one agent, well-managed context; split only when one of the four needs is measured, not felt.**

## The delegation summary: the artifact that replaces shared context

When agent A hands off to agent B, B does *not* inherit A's context — that would recreate the megatranscript with extra steps. B receives a **delegation summary**: a structured, provenance-carrying statement of what A concluded and what B should do.

```
DELEGATION from researcher-1 (trust: semi-trusted, agent-produced)
- Task assigned: find the remote work policy's approval deadline
- Conclusion: 48 hours in advance, per hr-remote-work v2 (2026-08-14)
- Evidence consulted: hr-remote-work-v2-c00, hr-remote-work-v2-c02
- Uncertainty: none flagged; retrieval score 6.1
- Not found: contractor-specific rules (corpus lacks them)
```

Four properties make this an engineering artifact rather than a forwarded email: it is **structured** (a schema B can parse), **provenance-carrying** (B can re-check A's evidence, or cite it onward with the chain intact — Chapter 26 requires this), **uncertainty-explicit** (A states what it did *not* find, preventing B's confident filler), and **trust-labeled** — the key novel lesson of this chapter:

> **Agent output is neither trusted instruction nor raw evidence — it is semi-trusted data.** A downstream agent that treats another agent's conclusions as ground truth inherits that agent's every failure. A downstream that treats them as untrusted noise wastes them. The middle path is the label: usable as input, never as instruction, always re-checkable via provenance.

The failure shape this prevents has a canonical form: agent A hallucinates a "fact" in its summary; agent B treats summaries as facts; the final answer cites A's hallucination with full confidence — and *no layer ever re-derived it against the corpus.* Delegation summaries are DERIVED components (Chapter 3): labeled, bounded, and (in serious systems) spot-re-verified against their cited evidence (Chapter 28's audit pattern).

## Merging: where multi-agent goes to die

Parallel subtasks produce parallel results that disagree. The merge step — one context holding every delegation summary plus the original task — faces three cases our earlier chapters built the tools for:

- **Agreement with provenance** — merge trivially; cite all chains.
- **Conflict** — Chapter 18's rule transposed: *flag, never silently arbitrate.* Two agents returning different remote-day counts is a version/freshness bug until proven otherwise (Chapter 9's conflict detection), not a coin to flip in the merger's ranking.
- **Coverage gaps** — B's "not found" lines aggregate into the merge context's known-unknowns list, which either routes to a third agent or surfaces to the user as an honest limitation.

Merge contexts also need a budget: k delegation summaries × their size × the merge task's own needs — the Chapter 12 ledger applies unchanged, and the allocation report will tell you when your delegation summaries are too rich to afford.

## Worked example: planning the corpus-audit two-agent split

Task: audit the Nimbus corpus for governance gaps. Split: a **scanner agent** per access level (one sees only internal documents, one only security-restricted — Chapter 9's policies wired per agent), each producing delegation summaries with per-document findings and provenance; a **merge agent** that receives both summaries (never raw documents — the restricted scanner's *findings*, not its corpus, flow onward) and produces the audit report. Note what the architecture bought: the restricted documents were read by exactly one agent whose output was schema-bounded findings — the merge context never held raw restricted text, and the final report cites chains, not dumps. Now the counterfactual: run it as a single agent with everything. Compare total tokens, the answer, and *where the restricted text appeared* in every trace. If the outputs matched, the split bought isolation and parallelism and cost a merge step — the decision table writes itself.

## Exercises

1. **Beginner** — Write the delegation-summary schema for a research→drafter pair and the rendering rules (labeled, DERIVED, provenance visible). Compose one from the Chapter 21 research workflow's state.
2. **Intermediate** — Implement the conflict case: two scanner agents that return different numbers on overlapping topics; the merge agent must flag, then re-derive the value from the cited chunk ids (state has them) rather than choosing. Test both policies: coin-flip (forbidden) vs. re-derive.
3. **Advanced** — Write the decision memo: for a real (or invented) product task, argue single-agent vs. multi-agent using the four justifications and measured quantities (tokens, latency, failure modes, isolation needs). Include the merge cost explicitly, and the "what the demo hides" paragraph. Trade memos with another learner and attack each other's.

## Common failures

- **The shared-context "multi-agent."** All agents read one growing transcript — the megatranscript with more authors; the isolation benefit is zero and the cost is coordination.
- **Summary-as-truth.** Downstream agents consuming delegation summaries as facts; hallucination propagates with a citation attached. Provenance + spot re-verification is the cure.
- **Merge coin-flips.** Ranking resolving disagreements silently — Chapter 18's forbidden non-policy, wearing a new costume.
- **Agent count creep.** Starting with two agents "to be scalable" and reaching eight, each a new failure surface (Chapter 30 compounds). Split on need; merge on evidence.

## Summary

- Multi-agent is justified by isolation, parallelism, single-focus attention, and per-role tooling — measured, not felt; the default is one agent.
- Delegation summaries replace shared context: structured, provenance-carrying, uncertainty-explicit, trust-labeled as semi-trusted data.
- Merging is the hard part: conflicts flag and re-derive; known-unknowns aggregate honestly; budgets apply to summaries like anything else.

## Mastery checklist

- [ ] I can argue both sides of a split decision with the four justifications and name the merge cost.
- [ ] I can write a delegation summary whose trust label, provenance, and uncertainty are all machine-checkable.
- [ ] I can design the isolation boundary so restricted content appears in exactly one agent's context, and prove it from traces.

## Review questions

1. Why is agent output "semi-trusted," and what downstream behavior does that label mandate?
2. What does a delegation summary carry that a forwarded conclusion does not — and which chapter requires each?
3. Which of the four justifications does the corpus-audit example exercise, and what did it cost?

## References

- Anthropic, *Effective context engineering for AI agents* — sub-agent context isolation as a real pattern — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (reviewed 2026-10-20)
- Shinn et al., *Reflexion* — self-notes as bounded inter-agent context — https://arxiv.org/abs/2303.11366 (reviewed 2026-10-20)
- OpenAI, *Harness engineering* — environment design over prompt design for agent teams — https://openai.com/index/harness-engineering/ (reviewed 2026-10-20)

## Next

Chapter 23: multimodal context — images, audio, and their derived representations.

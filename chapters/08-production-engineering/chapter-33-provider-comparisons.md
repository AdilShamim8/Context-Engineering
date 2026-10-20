# Chapter 33 — Provider and Framework Comparisons

> Part VIII · Reliability, Performance, and Production · *Optional on first pass*
> Prerequisites: Chapter 30 · Status: complete
> Time: ~45 minutes

## Overview

The context-engineering ecosystem — model providers, retrieval stores, memory libraries, agent frameworks — is large, loud, and fast-moving. This chapter teaches comparison as an engineering method rather than a shopping exercise: the criteria, the baseline-first rule, and the verify-before-rely discipline for provider claims whose truth decays. The position up front: **you have already built the baseline; that is what makes comparison possible at all.** A team that never built the pipeline cannot evaluate a framework that promises to — they can only believe it.

## The criteria that matter

Evaluate every dependency on the same eight dimensions, in writing:

| Dimension | The question | Where you already have evidence |
|---|---|---|
| Capability | Does it actually do the thing, at your scale? | Golden suite, run against it |
| Complexity budget | What must your team now understand, debug, and upgrade? | Your pipeline's line count is the yardstick |
| Cost predictability | Pricing model, and what it does at 10×? | Ch. 31's ledger, re-run |
| Portability | If you remove it, what survives? | The component model (Ch. 3) is your portability insurance |
| Observability | Can you see *inside* it when it fails? | Ch. 29: if its failures are opaque to your traces, multiply its risk |
| Security posture | Trust boundaries, tenancy, logging behavior | Ch. 24–25 checklists applied to *its* architecture |
| Reliability semantics | Retries, idempotency, degradation control? | Ch. 30's ladder questions, asked of it |
| Maintenance velocity | Who fixes it when the provider beneath it changes? | Release notes as evidence; bus factor as risk |

The single most predictive dimension is **complexity budget**: most "productivity" frameworks spend it generously and return it as debug time. The second most predictive is **observability**: a component you cannot trace through is a component whose failures you will diagnose by superstition — exactly what this curriculum spent 29 chapters eliminating.

## The baseline-first rule

Never evaluate a framework against nothing; evaluate it against **your working baseline with its golden suite**. The method:

1. **Build the plain version first** (done — this curriculum's stack: ~2K lines of readable Python doing retrieval, selection, budgeting, assembly, memory, security, evaluation).
2. **Port one stage** to the candidate (its retriever, its memory store, its agent loop), behind your existing interface.
3. **Run the same suite.** Same cases, same metrics, one variable — Chapter 28's discipline, unchanged. Tokens, latency, and correctness all reported.
4. **Adopt only on evidence.** If the framework wins, you know *what* it bought and *what it costs* (its abstractions are now your complexity budget). If the baseline wins, you have earned the right to skip the framework — a decision most teams never get to make because they never built the baseline.

This rule protects against the ecosystem's strongest force: the demo-fallacy. Framework demos show the happy path on curated examples; your golden suite shows *your* conflict cases, refusal cases, and access cases — the behaviors (Ch. 27's categories) that demos don't test because demos aren't trying to be honest.

## Comparing model providers: the same table, different rows

Provider comparison is the criteria table applied to capability/cost/observability rows plus three provider-specific questions: **tokenization parity** (your estimates are calibrated per tokenizer — Ch. 2; switching drifts every budget), **positional and instruction-following behavior** (Ch. 13's protocol must re-run per provider), and **the integration surface** (what the request anatomy maps onto: instruction fields, document attachments, tool schemas — Ch. 0.2's four-part anatomy is your comparison checklist). The verify-before-rely rule applies double: provider capabilities (context caching mechanics, per-modality support, tool-calling shapes) change on vendor schedules, so every provider claim in your design docs carries a reviewed date and a re-verification trigger (Ch. 32's tuple rule).

## Framework categories, briefly and honestly

- **Retrieval stores** (vector DBs and hybrids): earn complexity when semantic-gap evidence exists (Ch. 7) and scale demands it. The decision data: your ablation showing lexical vs. semantic on *your* queries.
- **Agent frameworks**: orchestration conveniences around the loop you built in Ch. 21. The question is never "do we need agents?" — you have one — but "is their loop inspectable (traces), resumable (checkpoints), and degraded-ladder-compatible (Ch. 30)?" If yes, complexity may buy convenience; if no, it buys opacity.
- **Memory libraries**: verify against Ch. 18's requirements — provenance, conflicts flagged, TTL, deletion with audit. Most fail the audit-trail requirement quietly.
- **Eval platforms**: must be able to run *your* golden cases (the JSON grammar), not just their own dashboards. Harness independence (Ch. 27) is the requirement; a platform that forces its fixture format is a lock-in decision, priced as one.

## Worked example: the retrieval-store decision memo

Memo: "Should Nimbus Assistant adopt a vector store?" Evidence in hand: golden suite passes 12/12 lexical (the corpus is policy-shaped; queries are vocabulary-aligned; access filtering is the hard part and it's already enforced pre-ranking). A semantic ablation (Ch. 7's exercise) on 20 paraphrase questions shows lexical misses 4, semantic catches 3 of 4 — a real gap, *at a corpus size that fits in memory with brute-force scoring*. The memo's verdict: **not yet — adopt the `EmbeddingProvider` adapter interface now, revisit at 10× corpus or demonstrated user paraphrase pain; the deciding metric ships in the traces either way.** That is a decision that survives review because every clause cites evidence your own system produced. Compare it with the industry-standard memo ("everyone uses one"), which survives no review.

## Exercises

1. **Beginner** — Fill the eight-dimension table for *one* dependency you use (any stack, not just this one). Cite evidence for each row; mark each "believed, not measured" honestly.
2. **Intermediate** — Port the curriculum's retrieval to a different backend (a plain JSON store, a SQLite FTS index — anything behind `LexicalIndex`'s call shape) and run the golden suite unchanged. Report what the suite caught and what it couldn't.
3. **Advanced** — Write the adoption memo for the agent-framework decision on the Ch. 21 workflow: trace-compatibility, resume semantics, degradation ladder, and complexity budget, each scored with evidence from the framework's actual behavior in a spike. End with adopt/reject/defer and the trigger that reopens the decision.

## Common failures

- **Demo-driven adoption.** Frameworks chosen from launches and tutorials; the golden suite never consulted; complexity budget spent invisible.
- **Comparing to nothing.** Evaluating candidates against each other instead of against your baseline — you learn which vendor is loudest, not what you need.
- **Undated claims.** Provider capability notes without review dates; the doc lies by drift. Ch. 32's rule: every claim carries its review date.
- **Lock-in as surprise.** Adopting fixture formats and pipeline shapes that migrate your golden cases and component model out of your control — portability is Ch. 3's insurance; spend it knowingly.

## Summary

- Eight criteria, written evidence per row; complexity budget and observability are the most predictive.
- Baseline-first: port one stage, run your suite, adopt on evidence — the method is Chapter 28's, pointed at vendors.
- Provider comparisons re-run the Ch. 13 protocol and honor tokenization parity; every claim carries a review date.

## Mastery checklist

- [ ] I can fill the eight-row table with evidence or honest "believed" markers.
- [ ] I can port one stage behind an interface and run the unchanged suite on a candidate.
- [ ] I can write an adoption memo whose verdict cites evidence my system produced.

## Review questions

1. Why is "compare to baseline, not to competitors" the rule — what does baseline comparison expose that vendor comparison cannot?
2. Which two criteria are most predictive of later regret, and what is the mechanism in each case?
3. What must re-run when the provider changes, and why can't the deterministic suite see that class?

## References

- Method chapters: 27 (suite), 28 (ablation discipline), 13 (protocol), 31 (ledger), 32 (dated claims).
- Provider capability claims: verify against current provider documentation — this claim class changes frequently (noted 2026-10-20).

## Next

Part IX: the capstone — where everything you built becomes one system, and then becomes yours.

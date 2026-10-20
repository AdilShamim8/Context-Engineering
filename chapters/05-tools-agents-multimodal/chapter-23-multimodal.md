# Chapter 23 — Multimodal Context Engineering

> Part V · Tools, Agents, and Multimodal Context · *Optional on first pass*
> Prerequisites: Chapter 3 · Status: complete
> Time: ~40 minutes

## Overview

Documents are not always text: a benefits PDF embeds a table, a support ticket carries a screenshot, a meeting's decisions live in a recording. Multimodal context engineering is the discipline of deciding **which modality enters the request, in what derived form, at what cost** — and it is mostly a chapter about *derived representations* (Chapter 3's concept, now load-bearing). This chapter stays deliberately provider-neutral: capabilities differ across providers and change quickly, so every provider-specific claim here carries the verify-before-rely rule with today's review date.

## Raw input vs. derived representation: the load-bearing distinction

Almost every production decision in multimodal context is the same decision: does the model see the **raw artifact** or a **derived representation** of it?

| Artifact | Raw form | Common derivations |
|---|---|---|
| Photo of a whiteboard | image input | OCR'd text, extracted task list, description |
| Meeting recording | audio (rarely supported directly) | transcript, speaker-labeled notes, decisions list |
| Benefits PDF | document input | extracted tables, per-section summaries |
| Dashboard screenshot | image | metric extraction ("error rate 2.1%"), chart description |
| Video | frames / clip | keyframe summaries, event timeline |

The derivations are *text* — which means **everything Chapter 3 said about trust, provenance, and budget applies to them unchanged**, with one addition: the derivation itself is a transformation whose errors propagate. OCR garbles a digit, the transcription hallucinates a sentence, the frame summary misses the moment that mattered — and downstream, the model treats each as clean text with a confident provenance line. The engineering response is the same pattern as Chapter 6's ingestion honesty: derived representations carry their provenance *as derivations* (`DERIVED` kind, metadata naming the source artifact and method), and error-prone derivations (OCR, ASR) should be labeled with their method so downstream consumers can treat "300" from OCR with appropriate suspicion.

## Why derive at all? Three real reasons

1. **Budget and cost.** Raw images consume significant tokens per image under most provider pricing (numbers vary per provider; check current docs); an extracted table costs tens. When the task needs three numbers, derivation is the entire economics.
2. **Capability fit.** A transcription supports exact quote lookup and citation; the raw audio (where supported at all) supports vaguer references. When the task is "what did she commit to?", the derived form is the *task-fit* form.
3. **Provider independence.** Derived text outlives provider capability changes; raw-artifact pipelines re-validate every quarter.

And one honest counter-reason: **derivation loses.** The tone of a voice, the layout nuance of a diagram, the visual context of a photo — sometimes the task needs what extraction drops. The decision procedure is Chapter 12's, applied per artifact: what does *this step's task* need from *this artifact*? Answer first; choose raw or derived second; never "we have multimodal support, so attach everything."

## Modality-specific engineering, briefly

- **Images.** Ask what the task extracts (text? state? identity?) and prefer extraction-at-ingestion for stable artifacts (the Chapter 16 fragment logic: derived once, reused). Screenshots of UIs deserve structured extraction (field → value), not descriptions.
- **Audio.** Transcript with speaker labels and timestamps is the workhorse derived form; timestamps are the provenance that lets answers cite *moments* ("at 14:02 the customer agreed"). Without them, audio answers are uncheckable.
- **Video.** Rarely raw; almost always keyframes + timeline notes + selective transcript segments. Alignment between the transcript and the timeline is the make-or-break detail.
- **Tables and structured data.** Belong in context as *structured* representations (rows/keys), not as flattened sentences — Chapter 6's rule, unchanged.

**Alignment across modalities** is the quiet failure mode: the transcript says the decision was at 14:02 but the slide deck changed at 14:00; the derived forms disagree because they were derived at different times from different versions. Derivation timestamps in provenance metadata are how downstream stages can detect it.

## What this repository implements, and why it stops there

This curriculum's corpus is deliberately **text-only**, and the library implements no multimodal ingestion — an honest scope decision, not a gap: multimodal pipelines depend on provider capabilities and tooling that change fast, and teaching them deterministically offline would mean simulating OCR/ASR quality — fake errors teaching false lessons. What this repository *does* give you transfers completely: the derived-representation pattern (a `DERIVED` component with method + source provenance is modality-agnostic), the budget treatment (derived artifacts are just components in the ledger), the security treatment (an OCR'd form is untrusted content, Chapter 24 — scanned forms have been an injection vector in the wild), and the evaluation treatment (Chapter 27's coverage metrics score derived numbers like any other facts). The optional exercise below is where multimodality meets this corpus — through the pattern, not a provider.

## Exercises

1. **Beginner** — Take one real multimodal artifact you know (screenshot, recording). Write its derivation chain: raw artifact → method → derived text → provenance fields the derived component must carry. Where in the chain can a number silently change?
2. **Intermediate** — Implement the derived-note pattern in the library: a function that wraps extracted content as a DERIVED component with `{"derived_from": artifact_id, "method": "manual_transcription", "derived_at": ts}` and is rendered with that provenance visible. Test that the citation chain survives assembly.
3. **Advanced** — The multimodal eval design: write the protocol for measuring "transcription error → answer error" propagation. Pick (or simulate, clearly labeled) three transcript error types; design the golden cases that catch each; state which Chapter 27 metrics change and which are blind to it.

## Common failures

- **Attach-everything.** Multimodal support used as a budget firehose; the ledger shows it instantly.
- **Naked derivations.** OCR text entering context with no method/provenance — indistinguishable from authoritative text, and every error inherits trust.
- **Timestamp-less transcripts.** Unanswerable "when did they say it" follow-ups; audio provenance is alignment data or it is decoration.
- **Version-skewed derivations.** Two derived forms of one artifact, derived at different times, disagreeing silently — alignment timestamps are the detection mechanism.

## Summary

- Raw vs. derived is the recurring decision; derived forms are text and inherit all of Part I–VI's rules plus derivation-method honesty.
- Derive for budget, task-fit, and durability; keep raw when the task genuinely needs what extraction drops — decide per artifact, per step.
- Alignment metadata (timestamps, versions) is what keeps multiple derived forms of one artifact coherent.

## Mastery checklist

- [ ] I can decide raw-vs-derived for a given artifact and task, with the three reasons and the counter-reason.
- [ ] I can design the provenance fields a derived component must carry, and trace one failure each way (naked derivation; version skew).
- [ ] I can name which existing library mechanisms a multimodal pipeline reuses unchanged.

## Review questions

1. Why is OCR'd text *more* dangerous than typed text in context, and which label mitigates it?
2. What does "the derived form is the task-fit form" leave out — when is raw genuinely necessary?
3. Which two chapters' machinery does a transcript's timestamp provenance connect?

## References

- Provider multimodal capabilities (supported modalities, per-image token costs, document/vision APIs): verify against the *current* documentation of your specific provider before designing — this claim class changes frequently (noted 2026-10-20).
- Chapter 3 (DERIVED kind and trust inheritance), Chapter 6 (derived-representation honesty at ingestion), Chapter 27 (coverage metrics over derived facts).

## Next

Part VI: security — the part that has been running through every chapter so far, now at full strength.

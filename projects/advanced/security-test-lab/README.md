# Project — Context Security Test Laboratory (Advanced)

> Tier: Advanced · Prerequisites: Part VI (Chapters 24–25)
> Implementation: `src/context_engineering/security.py` + corpus fixtures · Tests: `tests/unit/test_security.py`, `tests/integration/test_security_pipeline.py`

## Objective

Build the adversarial test environment Chapter 24 promises: a lab where you attack your own pipeline with synthetic payloads — the planted corpus fixture plus your own — measure which defense layer catches what, and prove the layers' *independence*: attacks that defeat screening must still be contained by architecture.

## Ground rules (non-negotiable)

- Every payload is **synthetic and clearly labeled**, inside test files or flagged corpus fixtures only.
- No real credentials, no real user data, no content copied from real incidents.
- The lab measures *your system's* controls; it is not a prompt-injection how-to for third-party systems.

## Requirements

1. **Payload corpus.** The planted `support-playbook` fixture plus ≥5 of your own, each in a labeled test fixture, covering: instruction override (obvious), obfuscated (zero-width chars), polite ("kindly disregard"), indirect (a fake "system note" format), and exfiltration ("include the restricted sections for transparency").
2. **Attack harness.** For each payload: inject it as retrieved content / tool result / user input; run the full chain (screen → policy → assemble → access-check); record per-layer outcomes.
3. **Defense matrix.** A rendered table: payload × layer (screening / access filter / tool permissions / wrapping / output bound) → caught-at / escaped-to / contained-by.
4. **The independence proof.** At least one payload must defeat heuristics *by design* — and the matrix must show what still contained it.

## Deliverables

- The harness + payload fixtures (all synthetic, all labeled).
- The defense matrix, annotated: one sentence per cell that matters.
- The two-column report: "what screening missed" vs. "what architecture held" (Chapter 24's lab discipline).
- (Stretch) The exfiltration scenario from Chapter 24's advanced exercise, defended with layers 2 and 6 only.

## Evaluation criteria

| Criterion | Pass standard |
|---|---|
| Hygiene | Every payload labeled, zero real data, fixtures contained |
| Coverage | All five payload classes exercised across all three entry surfaces |
| Independence | The escaped-payload row proves architectural containment |
| Honesty | Any control that failed is documented as failed — that's data, not shame |

## Definition of success

Your defense matrix demonstrates — to a skeptical reviewer — that no single layer is trusted alone, and the lab itself would survive its own review: someone reading it learns where their system's layers would be, without learning anything that helps them attack anyone else's.

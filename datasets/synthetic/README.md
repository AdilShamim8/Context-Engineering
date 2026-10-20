# Nimbus Dynamics — Synthetic Knowledge Corpus

A **fictional** corporate knowledge base used across the entire curriculum. Every document, person, policy, date, and incident below is invented for teaching purposes. No real data, credentials, or individuals appear here.

## Why a governed synthetic corpus

Part II teaches that retrieval quality is bounded by corpus quality: versioning, freshness, access levels, ownership, and honest conflicts. The corpus below deliberately includes the failure modes Chapter 4 catalogued — a superseded policy still present, a stale document, restricted documents that must never leak into general answers, and one document containing a **synthetic prompt-injection fixture** for the Part VI security lab.

## Access levels

| Level | Meaning | Example documents |
|---|---|---|
| `public` | Available to anyone | (none yet — useful lab extension) |
| `internal` | All employees | HR policies, runbooks, guides |
| `restricted` | Named groups only (e.g., `security-team`, `hr-confidential`) | incident reports, compensation data |

Retrieval must **filter by access level before ranking** (Chapter 9). The golden evaluation suite includes questions whose correct behavior is *refusal* when the only relevant document is restricted.

## Directory contents

- `manifest.json` — the governance record: id, title, version, effective date, access level, owner, supersedence, and fixture flags for every document.
- `*.md` — the document texts.

## Governance notes (used by labs)

- `hr-remote-work` exists in **v1 (2024, superseded)** and **v2 (2026, current)**. Version-aware retrieval must return v2 only; both are kept so learners can watch naive retrieval produce Lab 00's "confident, citable, wrong" failure.
- `data-retention-schedule` is intentionally aging — it anchors freshness exercises (Chapter 9).
- `support-playbook` contains a clearly-marked synthetic injection fixture in one section. The manifest flags it (`"synthetic_injection": true`); Part VI screens and wraps it. It exists to be attacked in a controlled lab, never to be obeyed.
- `hr-compensation-bands` and `security-incident-report-2026-07` are `restricted`: correct pipelines never hand their content to a general user's model context.

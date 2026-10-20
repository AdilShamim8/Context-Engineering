# Chapter 32 — Deployment, Monitoring, and Maintenance

> Part VIII · Reliability, Performance, and Production
> Prerequisites: Chapter 30 · Status: complete
> Time: ~50 minutes

## Overview

A context system's behavior is a function of *four* evolving inputs — code, corpus, configuration, and model — and maintenance is the discipline of keeping them coherent while all four drift. This chapter covers configuration and secrets, versioned deploys with regression gates, monitoring and rollback, source updates as release events, and the specific maintenance cadences (corpus review, case staleness, model updates) that keep a context system honest after the novelty wears off.

## Configuration is behavior; secrets are never config

The stack's tunables — budgets, priorities, thresholds (`min_coverage`, `max_items`), policies (freshness, access), feature flags for context variants — are all *behavioral parameters*: change them and the golden suite is the only honest way to know what changed. The deployment discipline follows: **config changes are code changes** — versioned, reviewed, and regression-gated like code (the suite runs in milliseconds offline; there is no environment excuse). The corpus's own feature-flag guide (fiction, faithfully reflecting production practice) teaches the pattern: flags with owners, expiry dates, defaults that define failure behavior.

Secrets are categorically different: API keys live in a proper secrets manager or environment injection — never in code, never in committed `.env` files (the repo's `.env.example` pattern), never in traces or logs (Chapter 29's redaction exists for the accidental case). The blast-radius rule from Chapter 24 applies: a credential in a config file is one `git commit` from being a public credential; treat any exposure as a compromise — revoke first, clean history second, investigate third.

## Deploy = four-way version lock

Deploying a context system means shipping a coherent tuple: **(code version, corpus version, config version, model version)**. The regression gate runs before the tuple ships:

```
code change      → unit + integration + golden suites
corpus change    → manifest consistency + version-selection + golden staleness (Ch. 28)
config change    → the same golden suite, against the new tuple
model change     → n-repeat model runs (Ch. 28) + grounding checks + latency/token re-baseline
```

Note the last line: **model updates are regression events.** A new model version changes tokenization (your estimates drift), positional behavior (Ch. 13's curve may flatten or sharpen), instruction-following (your instructions may need re-tuning), and cost. Pin model versions explicitly; treat provider deprecation notices as scheduled maintenance, not surprises; and re-run the *model-dependent* protocols on every bump because the deterministic suite (correctly) cannot see this class of change.

## Monitoring: the four families, alerting on two

Chapter 29's metric families become the monitoring stack: per-stage latency (p95), token usage per kind (the history-drift detector), failure/degradation rates (fallback engagement is your silent-quality-loss alarm), retrieval behavior (bimodal hits = vocabulary regressions). The alerting discipline: alert on **degradations and drift** (which mean silent quality loss) and **latency/error SLO breaches** (which mean user pain); report but don't alert on the noisiest series — alert fatigue is how real regressions get ignored (Ch. 29's exercise concludes here).

One monitoring category deserves its own mention: **grounded-quality sampling.** A small random sample of production answers (redacted per Ch. 25/29) scored against golden-style rubrics — a few per day, human or model-assisted — is the only monitor that catches the failure the metrics miss: correct-looking wrong answers after a corpus or model drift. It is the maintenance habit that most teams skip and most incidents require.

## Rollback: the tuple rewinds

Rollbacks must rewind the *tuple*, not just the code: the corpus revert comes with its golden-case revert (the cases pin the old facts); the model revert re-enables the old token/latency baselines; the config revert is a commit. Chapter 16's invalidation hooks matter here: a rolled-back corpus must invalidate caches keyed on corpus_version — the mechanism already exists, because the key was designed with this moment in mind. The drill: rehearse the rollback in staging with the same scripts as prod; the rollback that was never rehearsed is a hypothesis, not a plan (Chapter 30's ladder discipline, at deployment granularity).

## Source updates as releases

The corpus is load-bearing infrastructure (Ch. 26), so ingestion of *updates* follows release semantics: batched into reviewable changes (Ch. 28's one-commit rule), gated by the suite, announced to consumers whose golden cases pin the old world, and rolled out with the same canary patience as code — because for the users asking questions, a corpus change *is* a behavior change. The chapter's one-line summary of the whole discipline: **for the user, there is no difference between a code change and a corpus change and a model change — only between yesterday's answers and today's.** Your release process must be equally indifferent to which artifact moved.

## Worked example: the hr-vacation v4 release

People-ops publishes v4 (carryover window clarified). The release: edit document + bump manifest (`supersedes: v3`) + run suite → gc-02 fails on the old "5" (correctly — staleness detection working as designed) → update gc-02's required fact to v4's text in the same commit → suite green → deploy with corpus_version change → caches keyed on corpus_version invalidate on arrival → the trace's `dropped=hr-vacation-v3-c*` line confirms v3 is no longer reachable → the grounded-quality sample this week shows carryover answers citing v4. Rollback rehearsal: revert the commit (document, manifest, case together) — the tuple rewinds coherently. The whole story happened as one reviewable change, which is the standard.

## Exercises

1. **Beginner** — Write the runbook page for a corpus release on the Nimbus stack: pre-checks, the commit contents, the gate, the post-deploy verification, the rollback. Rehearse it once on a scratch copy.
2. **Intermediate** — Build the config-mutation test: parameterize the capstone pipeline's budget and selection knobs from a JSON config file; write the test that loads two configs and runs the golden suite under both, asserting which cases differ. Config changes now *cannot* land ungated.
3. **Advanced** — The model-bump protocol: script the Chapter 28 model-dependent rules (n repeats, variance report, grounding checks, token/latency re-baseline) as an executable runbook against the optional model adapter boundary. Dry-run it with the deterministic responder standing in for the model, and report what the protocol would catch if the stand-in were replaced by a subtly worse model.

## Common failures

- **Config as YAML folklore.** Parameters changed in production by hand; no version, no gate, no regression story. Config is code.
- **Secrets in the wrong layer.** Keys in env-files committed "temporarily," tokens in traces "for debugging" — both are Chapter 24/25 incidents waiting for their disclosure moment.
- **The untested rollback.** Rollback documented but never rehearsed; the first real incident discovers the corpus cases don't revert with the code.
- **Model drift as ambient weather.** Provider updates arriving silently; behavior shifts attributed to "the model being weird lately." Pin versions; regression-gate bumps.

## Summary

- Four evolving inputs (code, corpus, config, model) ship as one versioned tuple; every change class has its gate, and model bumps are regression events.
- Monitor degradations and drift; alert on SLO breaches; sample grounded quality — the only monitor for confident-wrong answers.
- Rollback rewinds the tuple; source updates are releases; config is code; secrets are never either.

## Mastery checklist

- [ ] I can write and rehearse the corpus-release runbook, including the golden-case update in the same commit.
- [ ] I can gate config changes with a mutation test that names the affected cases.
- [ ] I can script the model-bump protocol with variance and re-baselines.

## Review questions

1. Why must the rollback revert golden cases along with the corpus — what breaks if they revert alone or not at all?
2. Which monitoring family catches "correct-looking wrong answers," and why can't the others?
3. What makes a model update a regression event even when the provider calls it an improvement?

## References

- Patterns from this repository: `.env.example`, manifest versioning, `corpus_version` in the golden suite, Chapter 16's cache keys, Chapter 28's gating flow.
- OWASP GenAI Security Project — deployment and configuration risk framing — https://genai.owasp.org/ (reviewed 2026-10-20)

## Next

Chapter 33: the ecosystem — providers and frameworks, compared the engineering way.

# Security Policy

## Scope

This repository is an **educational resource**. It contains a reference implementation of context-engineering concepts, synthetic datasets, tests, and documentation. It is not a production system, and its examples are not production-hardened.

Security-relevant areas of this repository:

- The trust-boundary model (`src/context_engineering/security.py`): trusted instructions vs. untrusted retrieved content.
- Access-aware retrieval (`src/context_engineering/provenance.py`): filtering by access level *before* context assembly.
- Heuristic screening for prompt-injection payloads in untrusted content.
- Log redaction helpers.
- The synthetic security test lab (`projects/advanced/security-test-lab/`).

## Important honesty statement

**Heuristic screening is a detection aid, not a security boundary.** No screening rule, and no natural-language instruction inside a prompt, can guarantee protection against prompt injection. This repository teaches layered, application-level controls — trust labeling, access filtering before assembly, least-privilege tools, output validation — precisely because instruction-level defenses are insufficient. Any chapter text or code comment claiming more than this is a bug worth reporting.

## Reporting a vulnerability

If you find a security-relevant flaw in this repository's own code or content (for example, a way the demonstration code mishandles untrusted input, or committed secrets):

1. **Do not open a public GitHub issue** with exploit details.
2. Use GitHub's *Report a vulnerability* option (Security → Advisories) on this repository, or contact the repository owner through their GitHub profile.
3. Include: a description, a minimal reproduction, affected paths, and — if you have one — a suggested mitigation.

Expect acknowledgement within a reasonable window; this is a learning project, not a staffed product.

## Credential policy

- No credentials, tokens, or personal data may ever be committed. `.gitignore` excludes `.env` and `.env.*`.
- If a credential appears in the repository or in a conversation about it, treat it as **compromised**: revoke it immediately at the provider, then clean history. Review the account for unexpected activity.
- All example data is synthetic. The Nimbus Dynamics corpus, its "employees," and its "policies" are fictional.

## Secure-use expectations

If you adapt code from this repository into a real system:

- Enforce authorization in your data layer before anything reaches a model context; do not rely on prompt instructions for access control.
- Redact logs by default; context traces may contain user data.
- Rate-limit and bound tool execution (the educational orchestrator demonstrates the shape of these controls, not production-grade implementations).
- Keep provider credentials in a proper secrets manager, never in environment files committed to repositories.

# Contributing to Context-Engineering

Thank you for considering a contribution. This repository is a learning environment, so the bar for content is not "long" but **correct, reproducible, and educational**.

## Ways to contribute

- **Chapter improvements** — clearer explanations, better diagrams, updated sources. Technical claims must carry a review date and a verifiable source.
- **New exercises and labs** — especially adversarial/edge cases for the existing evaluation suites.
- **Adapter implementations** — optional integrations (exact tokenizers, embedding providers) behind the existing interfaces in `src/context_engineering/`. Adapters must remain optional: nothing in the core curriculum may depend on them.
- **Bug reports and fixes** — include a failing test case with the fix.

## Ground rules

1. **Standard library only** for `src/context_engineering/` core modules. Third-party code stays behind optional interfaces.
2. **Synthetic data only.** Never add real documents, user data, credentials, or personal information. All fixtures remain fictional (the Nimbus Dynamics corpus).
3. **Deterministic first.** If a concept can be demonstrated without a model API, it must be. Model-dependent additions are marked and optional.
4. **Tests required** for any code change. `python -m unittest discover` must pass.
5. **No secrets.** A pre-commit habit: `git diff --cached | grep -E "ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|api[_-]?key\s*="` should find nothing. A leaked credential means it is already compromised — rotate it immediately.

## Workflow

1. Fork or branch from `main`.
2. Make one coherent change per commit (a chapter, a module + tests, a lab).
3. Run the checks below.
4. Open a pull request describing what the change teaches or fixes and how you verified it.

```bash
# Checks before every commit
python -m unittest discover

# Optional: quick CLI smoke test
python -m context_engineering.cli --help
```

## Documentation conventions

- Chapters follow the established structure (overview → concepts → diagrams → worked example → implementation → exercises → failures → checklist → references) and live in `chapters/<part>/`.
- Mermaid diagrams must reflect the actual implemented architecture, not aspirational components.
- Every external source is listed with a review date in `references/`.
- Terms are used consistently with `glossary/glossary.md`; add new terms there when you introduce them.

## Commit style

Use a short, specific message with an area prefix, e.g.:

```
feat(part-3): add chapter 13 ordering experiment protocol
fix(memory): purge_expired now honors ttl_days=0
docs(part-6): clarify that instruction-level defenses are insufficient
```

## Licensing note

The repository currently has **no license** (see `docs/audit/2026-10-20-audit.md`). By submitting a contribution you agree it may be licensed under whatever license the repository owner ultimately selects.

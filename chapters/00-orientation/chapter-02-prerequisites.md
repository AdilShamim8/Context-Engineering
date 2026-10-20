# Chapter 0.2 — Prerequisite Knowledge

> Part 0 · Orientation
> Prerequisites: none · Status: complete
> Time: ~30 minutes (longer if filling gaps)

## Overview

This chapter states the minimum background needed for the curriculum, gives a fast refresher on the one topic most learners are missing (how a language-model request actually looks on the wire), and points to where to fill deeper gaps. The full self-assessment lives in `docs/prerequisites.md`; this chapter covers the essentials inline so the curriculum never sends you elsewhere for core material.

## What you actually need

1. **Working Python** — functions, dicts/lists/sets, `dataclasses`, basic `re`, `json` module. Every library module uses dataclasses for inputs/outputs and pure functions for logic. If you can read this snippet, you are fine:

```python
@dataclass
class Candidate:
    text: str
    score: float

ranked = sorted(candidates, key=lambda c: c.score, reverse=True)
```

2. **JSON** — manifests, evaluation cases, and checkpoints are JSON. You need `json.loads`/`json.dumps` comfort.

3. **HTTP at concept level** — what a request/response is, what an API key is, why keys are secrets. Nothing in the core curriculum calls the network.

4. **An inverted index, conceptually** — the idea of "word → list of documents containing it." Part II implements it in ~50 readable lines; knowing the concept beforehand makes it click instantly.

5. **Git basics** — clone, commit, push, read a diff. The repository's own history is deliberately structured as reviewable units you can learn from.

## Fast refresher: what a model request actually is

This is the piece learners most often fake their way through, and the entire curriculum sits on it, so here it is without hand-waving.

When your application "calls a model," it composes a request — typically over HTTPS — whose body is, conceptually:

```json
{
  "instructions": "You are Nimbus Assistant. Answer only from the provided documents...",
  "messages": [
    {"role": "user", "content": "How many remote days per week are allowed?"},
    {"role": "assistant", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "documents": ["...retrieved text..."],
  "tools": [ {"name": "search_confluence", "schema": "..."} ]
}
```

Provider APIs differ in names and shapes, but the anatomy is shared: **instructions, prior conversation, retrieved or attached content, tool definitions**. Everything the model will ever "know" for this call is in this request. It has no other window onto your application, your database, or the truth. When the answer is wrong, the *first* question is always: what, exactly, was in this request? Not "why is the model dumb?"

**Key consequences you will use all curriculum long:**

- If evidence is missing from the request, the model cannot use it. It will guess — fluently and confidently (a hallucination is a confident guess without a source).
- If stale and fresh evidence are both present without labels, the model has no reliable way to prefer the fresh one.
- If the request is too large, something must be dropped — by you, deliberately, or by the provider, silently.
- If untrusted text (a retrieved web page, a document) is inside the request, the model may treat it as instructions unless your system design prevents that.

## What you do NOT need

- Machine learning theory, gradients, or fine-tuning knowledge.
- A vector database, a paid API, or any cloud account.
- Prior RAG/agent framework experience — frameworks are compared in Chapter 33, but only *after* you build the concepts from scratch.

## Gap-filling pointers

- Python `dataclasses`/`re`/`json`: the standard library docs for these three modules are short and sufficient.
- HTTP: any 15-minute "what is an HTTP request" explainer; you need concepts, not cURL skills.
- Inverted index: read the first section of Wikipedia's "Inverted index" article; or simply trust Part II to build it in front of you.

## Exercises

1. **Beginner** — Without looking, write the four anatomical parts of a model request from memory. Check against the refresher.
2. **Intermediate** — Take the JSON snippet above and mark each part as *application-controlled* (you decide) vs. *runtime-dependent* (provider rules apply). Keep your answer for Chapter 3.
3. **Advanced** — Describe one scenario where the model request is missing evidence yet the model answers plausibly. What should a well-engineered system do instead?

## Mastery checklist

- [ ] I can write the anatomy of a model request from memory.
- [ ] I understand "the model sees only the request" and its four consequences.
- [ ] I have honestly assessed my Python/JSON/HTTP/Git readiness.

## Next

`chapter-03-environment-setup.md` — set up, run the tests, and run the first experiment.

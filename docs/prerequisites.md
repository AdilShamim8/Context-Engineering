# Prerequisite Knowledge

Context Engineering sits on top of a few practical software skills. You do not need to be an expert in any of them, but you need working familiarity. This page helps you self-assess and fill gaps efficiently. It deliberately avoids becoming a programming textbook — each section points at what "enough" looks like for this curriculum.

## The self-assessment

Try to answer each question honestly. Where you hesitate, use the short refresher pointer; where you cannot answer at all, spend an evening on the linked topic before Part I.

### 1. Python fundamentals (required)

You should be able to:

- Write functions with default and keyword arguments.
- Use the core containers: `list`, `dict`, `set`, `tuple` — including dict/set comprehension basics.
- Read and write `dataclasses` (they appear in nearly every library module).
- Work with `str` methods and simple `re` regular expressions (`\w+`, `\s+`, case-insensitive flags).
- Read a `with open(...)` block and understand context managers as a *language feature* (unrelated to our topic, same word).
- Run tests with `python -m unittest`.

Refresher focus: `dataclasses`, `enum`, `re`, `json`, and `pathlib` from the standard library. Roughly one evening of review covers everything the curriculum uses.

### 2. JSON and structured data (required)

You should be able to:

- Read a nested JSON document and describe its structure.
- Convert between Python dicts/lists and JSON strings (`json.dumps` / `json.loads`).
- Explain the difference between a JSON object, array, and scalar.

Why it matters here: manifests, evaluation cases, checkpoints, and traces are all JSON. If you can read the repository's `datasets/synthetic/corpus/manifest.json` and describe what each field means, you are ready.

### 3. HTTP and APIs (required at concept level)

You should be able to:

- Explain what an HTTP request is: method, URL, headers, body.
- Say what an API key is and why it must never be committed.
- Describe what a JSON-over-HTTP API call looks like conceptually.

You do **not** need to call any external API in this curriculum — everything is local — but tool-context engineering (Part V) assumes you understand what a tool call *is*.

### 4. Data structures basics (required)

You should be able to:

- Explain hashing and why set/dict lookups are fast.
- Explain what an inverted index is at a conceptual level (word → list of documents containing it). Part II builds one in ~50 lines; understanding the concept first makes it obvious.

### 5. Git basics (required)

You should be able to:

- Clone, commit, push, and read `git log` / `git diff`.
- Explain what a diff and a commit message are for.

This repository's own history is a teaching artifact: each commit is a coherent, reviewable unit.

### 6. LLM concepts (required at orientation level)

You should be able to answer:

- What is a token, loosely? (Chapter 2 makes this precise.)
- What does "the model sees only what you send it" mean?
- Why can a model confidently state something false? (It predicts plausible text; it does not look up truth.)

If these are unfamiliar, read `chapters/00-orientation/chapter-02-prerequisites.md` — it covers exactly the LLM background needed and nothing more.

### 7. Testing concepts (helpful, not blocking)

Familiarity with "arrange, act, assert" and with reading a `unittest.TestCase` helps but is picked up naturally in Part II onward, since every module ships with readable tests.

## What you do NOT need

- **No machine-learning background.** The curriculum treats models as capable-but-literal reasoning components whose behavior you engineer around; no math is required.
- **No web-framework experience.** Nothing is built on Django/Flask/Next.js.
- **No vector-database experience.** Part II explains when you need one and implements retrieval without one.
- **No paid API access.** Core content is deterministic and offline. Model-dependent exercises are optional and clearly marked.

## Minimum viable checklist

You are ready for Part I when you can:

- [ ] Write and run a Python script with a dataclass, a dict comprehension, and a regex.
- [ ] Parse a JSON file and print a nested field.
- [ ] Explain request/response in one sentence.
- [ ] Clone a repository and read its commit log.
- [ ] Say what a token is in one sentence and why API keys are secrets.

That is genuinely all. Everything else — retrieval theory, memory policies, evaluation methodology — this repository teaches from first principles.

# Learning Guide

How to actually use this repository well. The full curriculum specification lives in [`CURRICULUM.md`](../CURRICULUM.md); this page is about study method.

## The core idea

Context Engineering is a *decision* discipline. Every chapter ultimately teaches you to answer variations of one question: **what information does the model need for this step, and what must it not see?** The mechanical skills — chunking, scoring, budgeting, compressing — exist to serve that decision. If you finish a chapter able to explain *why* a technique helps and *when it backfires*, you have succeeded, regardless of how much code you memorized.

## Recommended path

1. **Do not skip Part 0.** Run the test suite and the first experiment before reading theory. Having a working environment changes how theory sticks.
2. **Read chapters in order within a part.** Parts are ordered by dependency; inside a part, later chapters assume earlier ones.
3. **Read actively.** Each chapter has exercises at three levels. Do at least the beginner one for every chapter and one intermediate exercise per part.
4. **Run the code while reading.** Chapters reference library modules; open them, read the docstrings, and call them from a REPL. The library is small enough to read end-to-end.
5. **Do the labs.** Labs are where the longitudinal example — the Nimbus Dynamics knowledge base — grows chapter by chapter. You watch one system evolve instead of juggling disconnected examples.
6. **Close each part with its project or lab deliverable** and the part's completion criteria from `CURRICULUM.md`.

Realistic effort per part: 3–6 hours for Parts 0–I, 6–10 hours for Parts II–III, 4–8 hours for each of Parts IV–VII, and open-ended for Part IX. Treating it as a semester-length course at a few hours per week works well.

## How notes, code, labs, and projects fit together

| Artifact | Role | Where |
|---|---|---|
| Chapter notes | Teach concepts, trade-offs, and diagnosis | `chapters/` |
| Library modules | Reference implementation you read, run, and extend | `src/context_engineering/` |
| Labs | Short, guided, verifiable exercises tied to chapters | `labs/` |
| Projects | Larger builds that produce portfolio deliverables | `projects/` |
| Tests | The ground truth for expected behavior; extend them in exercises | `tests/` |

A single workflow appears repeatedly: **retrieve candidates → filter by access and freshness → screen untrusted content → select by relevance → allocate budget → assemble with labels → execute → evaluate**. Every part of the curriculum deepens one or two stages of that pipeline. By the capstone you will have implemented it end-to-end and measured it.

## The evaluation mindset

Two habits separate context engineers from prompt tinkerers:

1. **Inspect what was assembled.** Never guess what the model saw. Use the context inspector to look. Most "model is confused" problems are "context is wrong" problems.
2. **Change one thing, measure, repeat.** The evaluation harness exists so you never have to argue from vibes. Golden cases, ablations, and reports are first-class citizens from Part II onward — not an afterthought.

## Deterministic vs. model-dependent exercises

Exercises that use the deterministic responder are labeled as such: they demonstrate *mechanical* context effects (what fits, what gets dropped, what gets cited) and are fully reproducible. Exercises marked **model-dependent** need a real LLM and produce variable results; treat their outputs as evidence to reason about, not ground truth. No chapter requires a paid API to complete its core learning objective.

## If you get stuck

- Re-read the chapter's *Common failures* section — most stuck points are listed there.
- Read the test suite for the relevant module: tests document exact expected behavior.
- Check `docs/development-guide.md` for how to run and extend things.
- The glossary (`glossary/glossary.md`) resolves terminology; terms are used consistently with it throughout.

## Tracking your own progress

Each chapter ends with a mastery checklist. Keep a simple learning journal: for each chapter, one sentence on what you learned and one open question. Review open questions at the end of each part; if a question persists, it usually points to a prerequisite gap worth revisiting.

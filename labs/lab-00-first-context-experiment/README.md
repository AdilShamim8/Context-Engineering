# Lab 00 — First Context Experiment

> Time: ~30 minutes · Deterministic · No dependencies
> Chapter tie-in: 0.3 · Success criterion: all three scenarios run and scenario 3's danger is explained in your own words

## Objective

Observe, in the most literal way possible, that **the context supplied to a responder determines the answer** — including confident, citable, wrong answers built on stale evidence.

## Instructions

1. Run the experiment:

   ```bash
   python labs/lab-00-first-context-experiment/experiment.py
   ```

2. For each of the three scenarios, write one sentence: *what changed in the context* and *what changed in the answer*.

3. Answer the lab questions (below) before reading the solution notes in `chapter-03-environment-setup.md`.

4. Complete the beginner exercise from Chapter 0.3: add a contradictory document to scenario 2 and predict the outcome before running it.

## Lab questions

1. In scenario 3, is the responder "wrong"? Justify your answer using the notion of *available information* rather than the notion of correctness.
2. The citation in scenario 2 comes from metadata (`version`, `effective date`), not from the document text. Why does that matter for Part II?
3. If a real language model replaced the rule-based responder, which scenarios would become *harder* to reason about, and why?

## Deliverables

- The experiment output (three scenarios).
- Written answers to the three lab questions.
- Your prediction and observation for the contradiction exercise.

## Definition of success

All scenarios run without error; your three sentences correctly identify *context change → answer change* in each; and your answer to question 1 names the real failure — **the system supplied stale information**, not "the model messed up."

## Notes

- Everything here is synthetic. Nimbus Dynamics, its policies, and its dates are fictional.
- This lab is self-contained on purpose: the production versions of these ideas live in `src/context_engineering/` (starting Part I) — this file is a controlled, readable first exposure, not the reference implementation.

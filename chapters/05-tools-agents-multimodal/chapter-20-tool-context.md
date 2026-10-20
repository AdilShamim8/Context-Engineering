# Chapter 20 — Tool Context and External Interactions

> Part V · Tools, Agents, and Multimodal Context
> Prerequisites: Part III · Status: complete
> Time: ~60 minutes

## Overview

Tools turn a language model from a writer into an actor — and every capability you grant becomes a context-engineering surface twice over: the *definition* the model reads when choosing, and the *result* that enters context after execution. This chapter covers both: descriptions that teach selection, schemas that guard execution, permissions as architecture, output handling (pagination, truncation, summarization), and error results as context. `tools.py` implements the guarded path; its tests are the spec.

## Tool definitions are context, not documentation

A tool definition occupies the window (Chapter 2 taxes it) and competes for the model's attention with every other component. Four consequences, in descending importance:

1. **Descriptions teach selection, not usage.** The description's job is to answer *when should I pick this tool?* — including when **not**. "Check the employee calendar for availability. Use for scheduling questions only." The second sentence is worth more than any parameter documentation: it is the anti-hammer clause that keeps the tool from being picked because its name is friendly. (The failure it prevents has a name in the literature — excessive agency — and an OWASP category; reviewed 2026-10-20.)
2. **Fewer tools, chosen well, beat many tools.** Each added definition costs tokens *and* selection accuracy — tool choice is a decision problem, and more options mean more confusion risk. Ship the minimal set; add tools when the eval suite shows a real unmet need (Chapter 28's discipline transposed).
3. **Schemas are contracts.** Types and required fields do two jobs: the model gets an unambiguous calling convention, and — more importantly — the *application* validates arguments **before** anything executes. `validate_args` runs before the handler, always: malformed input must die at the boundary, not inside your production systems.
4. **Definitions are TRUSTED components.** They are application-authored (Chapter 3's trust axis), rendered as `TOOL_DEFINITION` components with `trust=TRUSTED` — in `spec_components()` you can watch the trust decision happen in code.

## The guarded path: what `ToolRegistry.call` enforces

Read `call()` top to bottom; the order is the security model:

1. **Unknown tool** → structured failure. The model cannot probe your surface by naming things.
2. **Authorization** — `required_access` checked against the *caller's* access set. Per-call, fail-closed, before validation and execution — Chapter 9's rule with hands. The check lives in the registry, not the prompt: a sentence like "you may only use allowed tools" is not an access-control list; this is.
3. **Schema validation** — wrong types, missing required, unknown parameters → structured failure with reasons (which enter context as readable error results, teaching the model to self-correct).
4. **Handler isolation** — exceptions are caught and converted to a generic failure ("tool execution failed: RuntimeError (details logged, not shown to model)"). Two properties matter: the process never crashes, and **internal details never enter model context** (a stack trace is an information leak that the model will faithfully quote).
5. **Output bounding** — outputs cap at `output_max_chars` with a visible truncation marker. The big-result failure (a 50KB API dump entering context and eating the budget) is prevented *structurally*.

## Tool results as context: the untrusted half

The result of a tool call is `TOOL_RESULT` — **untrusted** by Chapter 3's rule, whatever the tool's own trust level: a calendar tool returning a meeting note written by someone else is delivering content your app did not author. Results therefore get the full Chapter 24 treatment downstream: wrapped, labeled, screened. Two further design decisions:

- **Pagination and summarization over truncation.** The registry's cap is the safety net; the *policy* for big result sets should be structured pagination ("more available via `list_next(page_token)`") or extraction of the relevant fields (Chapter 14's pinned-fact compression) — not a blind character slice that cuts the payload mid-fact.
- **Errors are context worth crafting.** A structured error result ("invalid arguments: missing required parameter: date_range") is a *teaching signal* that lets the model retry correctly. A bare "Error" teaches nothing; a leaked stack trace teaches the wrong things. Error messages are prompt engineering for the next turn — design them like it.

## Worked example: the calendar tool, end to end

Register `calendar_check` (spec above), give an internal-level caller a bad call and watch the guarded path in the tests: wrong args → structured error with the missing parameter named → the model retries correctly → result truncated with a marker because the output cap fired → the assembly wraps it `UNTRUSTED` with its `TOOL_RESULT` label. Now give a public-only caller the same call: "caller lacks required access class 'internal'" — refused *before* validation, before execution, before any side effect. The four failure paths plus the success path are all visible in `tests/unit/test_tools.py`; run them, then modify one and predict the new behavior. That predict-then-verify loop is the chapter's real exercise.

## Exercises

1. **Beginner** — Write `ToolSpec`s for `search_docs(query, access_level)` and `file_read(path)` over the Nimbus corpus. For each: description with an anti-hammer clause, minimal schema, and the right `required_access`. Register and call them from the tests.
2. **Intermediate** — Implement the paginated tool: `search_docs(query, page_token)` returns 3 results plus a `next_token`. Then answer in writing: how does pagination interact with Chapter 15's progressive disclosure, and which failure does each approach cause?
3. **Advanced** — Build the excessive-agency test lab: register a `delete_document(doc_id)` tool with a plausible description, script a scenario where an injected "result" (Chapter 24 fixture) tells the model to call it, and demonstrate the *layers* that stop it: per-call permission, human-confirmation requirement you add, and bounded write-access the registry can't express alone. Write what the lab proves about prompt-level protection vs. architecture.

## Common failures

- **The 12-tool dump.** Every conceivable tool registered "for flexibility"; selection accuracy and budget pay for it. Add tools like stages: one at a time, with evidence.
- **Trusting tool results.** Results wrapped as raw assistant-visible strings with no label; an injected payload in a tool result becomes an instruction with hands (Chapter 24's indirect injection).
- **Leaky errors.** Stack traces and internal identifiers in error text; the model quotes them, users see them, and an attacker learns your internals.
- **Unbounded outputs.** One chatty API response silently eats 30% of the window; the budget report is where you catch it.

## Summary

- Definitions teach selection (anti-hammer clauses), cost window tokens, and are trusted; schemas validate before execution.
- The guarded path: unknown → unauthorized → invalid → isolated → bounded, each failure structured and instructive.
- Results are untrusted context: wrapped, labeled, capped — and designed (paginated/extracted) rather than sliced.

## Mastery checklist

- [ ] I can write a tool description whose anti-hammer clause I can defend, and count its token cost.
- [ ] I can recite the guarded path's five steps and their order's security meaning.
- [ ] I can design an error message that teaches the model to retry correctly without leaking internals.

## Review questions

1. Why does authorization precede validation in `call()`, and what would validating first leak?
2. Why are tool *definitions* trusted while tool *results* are untrusted — same tool, different trust?
3. What does an anti-hammer clause prevent, and where would you detect its absence in production traces?

## References

- OWASP LLM Top 10 — "excessive agency" and unsafe-tool-design categories — https://owasp.org/www-project-top-10-for-large-language-model-applications/ (reviewed 2026-10-20)
- Yao et al., *ReAct* — the act-observe loop these results feed — https://arxiv.org/abs/2210.03629 (reviewed 2026-10-20)
- Implementation: `src/context_engineering/tools.py`; tests `tests/unit/test_tools.py`.

## Next

Chapter 21: the loop itself — context across a multi-step workflow.

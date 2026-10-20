# Chapter 15 — Progressive Context Disclosure and Retrieval on Demand

> Part III · Dynamic Context Construction
> Prerequisites: Chapter 11 · Status: complete
> Time: ~45 minutes

## Overview

Progressive disclosure is compression's structural sibling: instead of shrinking content, **don't include it yet.** Give the model lightweight pointers (titles, summaries, identifiers, search results) and the tools to fetch details when a pointer earns it. This is the architecture behind "just-in-time retrieval" in agent practice (Anthropic's engineering guidance is the clearest public articulation; reviewed 2026-10-20) and behind Self-RAG's adaptive retrieval in research. It trades context bloat for extra tool calls, latency, and a new failure mode: the pointer that never gets followed.

## The two strategies, compared honestly

**Upfront loading** (everything possibly relevant, once): simpler control flow, one latency budget, easy to evaluate — and pays full price in tokens, noise cost (Chapter 2), position risk (Chapter 13), and security surface (everything sensitive is already in the request — Chapter 24 cares).

**Progressive disclosure** (pointers first, fetch on demand): requests stay small and sharply relevant; irrelevant documents never load at all (a *curation win that doubles as a security win*); and multi-hop questions work naturally (follow pointer → fetch → follow next). Costs: 2–5× the round-trips for deep chains, tool-call failure handling (Chapter 30), and — the real risk — **the model must choose to follow the pointer**. A model that answers from the pointer instead of the document is the progressive-disclosure failure shape: plausible summaries standing in for unread policy.

## Where it fits in the lifecycle

Chapter 10's steps 4–7 (retrieve → normalize → select → budget) become a *loop the model can drive*: stage one retrieves a **directory** (titles + section summaries + ids) sized to be cheap; the model's request includes the directory plus a `fetch_document(id)` tool; the model pulls what it needs; steps 3 and 8 (access filtering, labeled assembly) re-run **per fetch** — authorization is not a one-time gate but a per-tool-call check (Chapter 20 implements exactly this in `tools.py`).

## The pointer formats, cheapest first

- **Identifiers**: `fetch("hr-remote-work", version="2")` — cheapest, requires the model to already know the id means "the remote policy."
- **One-line descriptions** (the directory entry): `hr-remote-work v2 — 2 remote days/week, approval rules (internal)` — 15 tokens that prevent wrong fetches.
- **Summaries-as-pointers**: a 60-token compressed lead paragraph instead of the 600-token document — enough to answer *some* queries outright and to decide fetch-worthiness for the rest. (This is where Chapter 14 and this chapter meet: rung-5 notes as a first-class context artifact.)
- **Search results as pointers**: ranked hits with excerpts — the model fetches only promising lines, i.e., what search-driven agents have done since before it was fashionable.

## When progressive disclosure is the right call

It earns its complexity when: the candidate space is **large** (whole corpus in-context is impossible or noise-dominant); the task is **multi-hop** (upfront loading cannot know which document the *second* hop needs); or **cost/latency dominates** (small focused requests beat one mega-request on cache-unfriendly, token-metered APIs — see Chapter 16 for the interaction with prompt caching). It is the wrong call when: the corpus is small (fetch-the-whole-thing and select is simpler and sufficient — Part II's approach); the model is weak at tool choice (pointer-following becomes a capability lottery — Chapter 20); or every millisecond counts and an extra round-trip is unacceptable.

## Worked example: directory + fetch on the Nimbus corpus

Build it in the intermediate exercise, conceptually: `list_documents(access_policy)` returns one pointer line per *accessible* document (access filtering before the model sees even titles — the same Chapter 9 rule, now applied to the directory itself, because titles can leak); the request contains instructions + directory + `fetch_document`; each fetch re-checks the access policy and assembles a labeled, delimited EVIDENCE component (Chapter 24's wrapping, per-fetch). Watch the budget report: the multi-hop question "Does remote work policy restrict employees who relocate to another time zone, and which benefits cover that case?" loads exactly two documents instead of the whole corpus — and the tool-call trace (Chapter 29) shows every pointer the model chose *not* to follow, which is itself a diagnostic artifact: unfollowed high-value pointers are a prompt/tool-description quality signal.

## Exercises

1. **Beginner** — Write the directory-line format for all 12 corpus documents (respecting access: what does an internal-only user's directory *not* contain?). Count tokens: directory vs. full corpus.
2. **Intermediate** — Implement `fetch_document(doc_id)` as a `ToolSpec` (Chapter 20 will formalize; a plain function is fine now) with per-call access checking and labeled assembly. Run the worked example's question through it and diff the final context against the load-everything approach.
3. **Advanced** — Implement pointer-summaries: directory entries built by `extractive_compress` (60 tokens each). Measure: how many questions get answered from the directory alone? Where does answering-from-pointer produce *wrong* answers (the summary's loss budget vs. the question's need — Chapter 14 connect-back)? Report per-question: answered-from-pointer correctly / answered-from-pointer wrongly / fetched.

## Common failures

- **The unread pointer.** Model answers from a 15-token description instead of fetching; the answer inherits the description's every omission. Mitigation: descriptions that *refuse* to state facts (topic labels, not content), forcing facts to come from fetched documents.
- **Per-call authorization amnesia.** The first gate is enforced; the fetch tool forgets to check; restricted content rides the second hop. Tests must cover *every* tool, not the front door.
- **Fetch loops.** Pointer → fetch → new pointer → fetch… without a hop budget; latency and cost explode. Bound the loop explicitly (Chapter 30's bounded execution).

## Summary

- Progressive disclosure = pointers first, facts on demand: smaller, sharper contexts at the price of round-trips and a new failure shape.
- Pointers run from ids to compressed leads; directories are themselves access-filtered; authorization and labeling re-run per fetch.
- Right call for large candidate spaces and multi-hop tasks; wrong call for small corpora and latency-critical paths.

## Mastery checklist

- [ ] I can design a directory format whose entries cannot leak facts or access-restricted titles.
- [ ] I can implement per-fetch access checking and explain why one-time gating fails.
- [ ] I can name the failure shapes (unread pointer, fetch loops) and their mitigations.

## Review questions

1. Why is the pointer-directory a security surface, and which Chapter 9 rule applies to it unchanged?
2. When is answering-from-pointer correct design, and when is it a defect? What distinguishes the two?
3. Which tool-property (Chapter 20) bounds the fetch loop, and what does "bounded execution" mean operationally?

## References

- Anthropic, *Effective context engineering for AI agents* — just-in-time retrieval over upfront loading — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (reviewed 2026-10-20)
- Asai et al., *Self-RAG* — adaptive, on-demand retrieval — https://arxiv.org/abs/2310.11511 (reviewed 2026-10-20)
- OpenAI, *Harness engineering* — the environment that makes on-demand fetching productive — https://openai.com/index/harness-engineering/ (reviewed 2026-10-20)

## Next

Chapter 16: caching — making context cheap by not rebuilding it.

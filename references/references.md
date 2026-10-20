# References

Curated sources used and cited by the curriculum. Each entry carries the date it was last reviewed and what it is used for. Provider-specific facts (API names, limits, caching behavior, pricing) change frequently: the review date is the honesty marker — re-verify anything older than six months before relying on it operationally.

## Context engineering practice and guidance

- **Anthropic — *Effective context engineering for AI agents*** (engineering blog)
  https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  Used for: context-as-scarce-resource framing, compaction and structured note-taking, just-in-time retrieval, agent-context themes. Reviewed 2026-10-20.

- **Microsoft — *AI Agents for Beginners*, Module 12: Context Engineering***
  https://github.com/microsoft/ai-agents-for-beginners/tree/main/12-context-engineering
  Used for: beginner-level definitions and curriculum cross-checking. Reviewed 2026-10-20.

- **OpenAI — *Harness engineering: leveraging Codex in an agent-first world***
  https://openai.com/index/harness-engineering/
  Used for: the environment/harness perspective on agent context (what the system, not the prompt, supplies). Reviewed 2026-10-20.

## Long-context behavior (research)

- **Liu et al. — *Lost in the Middle: How Language Models Use Long Contexts*** (2023; TALA 2024)
  https://arxiv.org/abs/2307.03172
  Used for: the U-shaped positional effect in long contexts (Chapter 13). Cited qualitatively; effect sizes vary by model and task, so the curriculum teaches a measure-it-yourself protocol. Reviewed 2026-10-20.

- **Lewis et al. — *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*** (2020)
  https://arxiv.org/abs/2005.11401
  Used for: the original RAG formulation (Chapter 7 background). Reviewed 2026-10-20.

## Retrieval foundations

- **Robertson & Zaragoza — *The Probabilistic Relevance Framework: BM25 and Beyond***
  (Foundations and Trends in IR, 2014; origins in 1990s)
  Used for: the BM25 ranking function implemented in `retrieval.py` (k1, b parameters). Reviewed 2026-10-20.

- **Carbonell & Goldstein — *The Use of MMR, Habit-Based Diversity, and Re-Ranking*** (SIGIR 1998)
  Used for: maximal marginal relevance, the diversity principle in `selection.py`. Reviewed 2026-10-20.

- **Gao et al. — *Precise Zero-Shot Dense Retrieval without Relevance Labels* (HyDE)** (2022)
  https://arxiv.org/abs/2212.10496
  Used for: the query-transformation family of techniques (Chapter 8). Reviewed 2026-10-20.

- **Asai et al. — *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection*** (2023)
  https://arxiv.org/abs/2310.11511
  Used for: adaptive/on-demand retrieval (Chapter 15 discussion). Reviewed 2026-10-20.

## Agents, tools, multi-step systems

- **Yao et al. — *ReAct: Synergizing Reasoning and Acting in Language Models*** (2022)
  https://arxiv.org/abs/2210.03629
  Used for: the interleave-reason-and-act loop that Chapter 21's orchestrator simplifies. Reviewed 2026-10-20.

- **Shinn et al. — *Reflexion: Language Agents with Verbal Reinforcement Learning*** (2023)
  https://arxiv.org/abs/2303.11366
  Used for: self-verification and note-taking as agent context (Chapters 21, 22). Reviewed 2026-10-20.

## Security

- **OWASP — GenAI Security Project**
  https://genai.owasp.org/
  Used for: security risk framing across Part VI. Reviewed 2026-10-20.

- **OWASP — *Top 10 for Large Language Model Applications***
  https://owasp.org/www-project-top-10-for-large-language-model-applications/
  Used for: concrete risk categories (prompt injection, sensitive disclosure, excessive agency, etc.). Category lists are versioned; consult the current version. Reviewed 2026-10-20.

## Terminology notes

- The term **context engineering** in its current sense was popularized during 2025 through public discussion by Andrej Karpathy and Tobi Lütke; see Chapter 1 for the curriculum's position on this contested lineage. Public posts are volatile; rely on the archived engineering guidance above rather than social-media definitions.

## Scope companions

- **`Prompt-Engineering` (companion repository)** — https://github.com/AdilShamim8/Prompt-Engineering — owns instruction-writing technique.
- **`GenAI-Roadmap-with-Notes-and-Projects` (companion repository)** — https://github.com/AdilShamim8/GenAI-Roadmap-with-Notes-and-Projects — owns the broader GenAI journey, including a high-level context-engineering rung.

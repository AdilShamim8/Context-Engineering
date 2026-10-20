"""Command-line interface for the reference library (Projects 1–2, capstone).

Subcommands:

- ``budget``  (Project: Context Budget Explorer) — allocate the demo
  bundle under a context budget and print the full allocation report.
- ``inspect`` (Project: Context Inspector) — print every component's
  fate and the exact assembled request text, with span markers.

Later parts of the curriculum add:

- ``ask``      the deterministic knowledge assistant (Chapter 35)
- ``evaluate`` the golden evaluation suite (Chapter 27)

Run from the repository root, either with an editable install
(``pip install -e .``) or via ``PYTHONPATH=src`` — see
``docs/getting-started.md``.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from .assembly import OrderingStrategy, assemble
from .budget import AllocationResult, ContextBudget, allocate
from .context import ComponentKind, ContextComponent, SourceRef, TrustLevel


def load_bundle(path: str):
    """Load a component bundle JSON file into ContextComponents."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    components: list = []
    for entry in data["components"]:
        source = None
        if entry.get("source"):
            source = SourceRef(**entry["source"])
        components.append(
            ContextComponent(
                id=entry["id"],
                kind=ComponentKind(entry["kind"]),
                content=entry["content"],
                priority=int(entry.get("priority", 5)),
                trust=TrustLevel(entry.get("trust", "neutral")),
                source=source,
            )
        )
    return data, components


def _print_bundle_overview(components) -> None:
    print(f"{'ID':<26}{'KIND':<17}{'TRUST':<11}{'PRI':<5}TOKENS")
    for comp in components:
        print(
            f"{comp.id:<26}{comp.kind.value:<17}{comp.trust.value:<11}"
            f"{comp.priority:<5}{comp.token_count()}"
        )


def cmd_budget(args) -> int:
    data, components = load_bundle(args.bundle)
    budget = ContextBudget(
        total_tokens=args.total,
        reserved_output_tokens=args.reserved_output,
    )
    print(f"Demo bundle: {args.bundle} ({len(components)} components)")
    print(f"Question: {data.get('question', '')}")
    print()
    try:
        result = allocate(components, budget)
    except Exception as exc:  # BudgetError is the expected kind here
        print(f"ALLOCATION ERROR: {exc}", file=sys.stderr)
        return 1
    print(result.report())
    print()
    included = sum(1 for r in result.records if r.action == "included")
    truncated = sum(1 for r in result.records if r.action == "truncated")
    dropped = sum(1 for r in result.records if r.action == "dropped")
    print(f"Summary: {included} included, {truncated} truncated, {dropped} dropped")
    print(f"Context tokens used: {result.total_allocated} of {budget.available_for_context} available")
    return 0


def cmd_inspect(args) -> int:
    data, components = load_bundle(args.bundle)
    print("=== COMPONENTS ===")
    _print_bundle_overview(components)
    print(f"\nTotal bundle size: {sum(c.token_count() for c in components)} tokens")
    print()
    assembled = assemble(components, strategy=OrderingStrategy.KIND_GROUPED)
    print("=== ASSEMBLED REQUEST (kind-grouped ordering) ===")
    if args.mark_spans:
        lines = assembled.text.split("\n")
        for line in lines:
            marker = ""
            for cid, (start, _end) in assembled.spans.items():
                if start <= assembled.text.find(line) < _end and line.startswith("## "):
                    marker = f"   <-- {cid}"
            print(line + marker)
    else:
        print(assembled.text)
    print()
    print(f"Assembled size: {assembled.tokens} tokens (estimate)")
    return 0


def _resolve_repo_path(relative: str) -> str:
    """Resolve a default path against the CWD (commands run from repo root)."""
    if os.path.isabs(relative):
        return relative
    return relative


def cmd_ask(args) -> int:
    from .apps.knowledge_assistant import answer_question
    from .corpus import default_corpus_dir

    access = tuple(level.strip() for level in args.access.split(",") if level.strip())
    result = answer_question(
        args.question,
        access_levels=access,
        corpus_dir=default_corpus_dir(),
        screening_policy=args.screening,
    )
    print(result.summary())
    if args.show_context:
        print("\n=== ASSEMBLED CONTEXT ===")
        print(result.assembled.text)
        print(f"\n(assembled size: {result.assembled.tokens} tokens, estimate)")
    if args.show_trace:
        print("\n=== TRACE ===")
        print(result.trace.render())
    return 0 if result.answer.status in ("answered", "insufficient_evidence") else 1


def cmd_evaluate(args) -> int:
    from .apps.knowledge_assistant import golden_case_pipeline
    from .corpus import default_corpus_dir
    from .evaluation import load_cases, run_suite

    suite_path = args.suite or _resolve_repo_path(
        os.path.join("datasets", "synthetic", "golden", "golden_cases.json")
    )
    corpus_dir = default_corpus_dir()

    # The app caches its index per corpus dir; make sure it exists for the suite run.
    from .apps.knowledge_assistant import _index_for  # noqa: F401 (warm the cache)

    _index_for(corpus_dir)
    cases = load_cases(suite_path)
    report = run_suite(cases, golden_case_pipeline)
    print(report.render())
    return 0 if report.passed_count == report.total else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="context-engineering",
        description="Reference CLI for the Context Engineering curriculum.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_budget = sub.add_parser(
        "budget", help="Allocate the demo bundle under a context budget (Budget Explorer)"
    )
    p_budget.add_argument("--total", type=int, default=2000,
                          help="Total window tokens (default 2000 — deliberately tight)")
    p_budget.add_argument("--reserved-output", type=int, default=512)
    p_budget.add_argument("--bundle", default="datasets/synthetic/demo_bundle.json")
    p_budget.set_defaults(func=cmd_budget)

    p_inspect = sub.add_parser(
        "inspect", help="Print every component and the assembled request (Context Inspector)"
    )
    p_inspect.add_argument("--bundle", default="datasets/synthetic/demo_bundle.json")
    p_inspect.add_argument("--mark-spans", action="store_true",
                           help="Annotate component boundaries in the assembled text")
    p_inspect.set_defaults(func=cmd_inspect)

    p_ask = sub.add_parser(
        "ask", help="Ask the capstone knowledge assistant a question (deterministic, offline)"
    )
    p_ask.add_argument("question")
    p_ask.add_argument("--access", default="public,internal",
                       help="Comma-separated access levels for the caller (default: public,internal)")
    p_ask.add_argument("--show-context", action="store_true",
                       help="Print the exact assembled request")
    p_ask.add_argument("--show-trace", action="store_true",
                       help="Print the per-stage execution trace")
    p_ask.add_argument("--screening", choices=["label", "block"], default="label",
                       help="Security screening policy: label (default) or block")
    p_ask.set_defaults(func=cmd_ask)

    p_evaluate = sub.add_parser(
        "evaluate", help="Run the golden evaluation suite through the capstone assistant"
    )
    p_evaluate.add_argument("--suite", default=None,
                            help="Path to a golden case JSON file (default: the repository suite)")
    p_evaluate.set_defaults(func=cmd_evaluate)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

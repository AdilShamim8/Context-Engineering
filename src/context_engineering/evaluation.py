"""The evaluation harness: golden cases, coverage metrics, ablations (Chapters 27–28).

Evaluation philosophy encoded here:

- The harness is INDEPENDENT of the system under test. ``run_suite``
  takes a ``pipeline_fn(case) -> dict`` and knows nothing else about your
  system — deterministic responder, real model, or anything in between.
- Cases are DATA (JSON), not code: ordinary, edge, conflict, staleness,
  access-control, and no-evidence behaviors all live in one reviewable
  file with a corpus-version marker so staleness is detectable (Ch. 28).
- Failure messages name the missing fact / forbidden content / expected
  source — the report teaches, not just scores (Ch. 27's six levels:
  this module measures response-grounding; retrieval and selection
  quality are measured by their own metrics, not conflated here).

``evaluate_answer`` scores ONE level: the grounded-answer level. When
you adapt this harness, add metrics per level rather than stretching
these definitions (see Chapter 27's "not interchangeable" table).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class GoldenCase:
    """One evaluation fixture: question + expected grounding behavior."""

    case_id: str
    question: str
    required_facts: list = field(default_factory=list)   # substrings that must appear
    forbidden_facts: list = field(default_factory=list)  # substrings that must NOT appear
    expected_sources: list = field(default_factory=list) # source ids that must be cited
    should_refuse: bool = False                          # correct answer is a refusal
    access_levels: tuple = ("public", "internal")
    notes: str = ""


def load_cases(path: str) -> list:
    """Load golden cases from a JSON suite file."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return [
        GoldenCase(
            case_id=case["id"],
            question=case["question"],
            required_facts=list(case.get("required_facts", [])),
            forbidden_facts=list(case.get("forbidden_facts", [])),
            expected_sources=list(case.get("expected_sources", [])),
            should_refuse=bool(case.get("should_refuse", False)),
            access_levels=tuple(case.get("access_levels", ["public", "internal"])),
            notes=case.get("notes", ""),
        )
        for case in data["cases"]
    ]


@dataclass
class CaseResult:
    case: GoldenCase
    answer_text: str
    citations: list
    passed: bool
    failures: list
    tokens_used: int = 0

    def render(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        lines = [f"[{status}] {self.case.case_id}: {self.case.question}"]
        if self.failures:
            for failure in self.failures:
                lines.append(f"       - {failure}")
        if self.case.notes:
            lines.append(f"       note: {self.case.notes}")
        return "\n".join(lines)


def evaluate_answer(
    answer_text: str,
    citations: list,
    case: GoldenCase,
    tokens_used: int = 0,
) -> CaseResult:
    """Score one answer against its golden case."""
    failures: list = []
    lowered = answer_text.lower()

    if case.should_refuse:
        if "INSUFFICIENT" not in answer_text.upper():
            failures.append("expected a refusal, but the system answered")
    else:
        if "INSUFFICIENT" in answer_text.upper():
            failures.append("system refused, but evidence should exist for this question")
        for fact in case.required_facts:
            if fact.lower() not in lowered:
                failures.append(f"missing required fact: {fact!r}")
        for fact in case.forbidden_facts:
            if fact.lower() in lowered:
                failures.append(f"forbidden content present: {fact!r}")
        for source in case.expected_sources:
            if not any(source in citation for citation in citations):
                failures.append(f"expected source not cited: {source!r}")

    return CaseResult(
        case=case,
        answer_text=answer_text,
        citations=list(citations),
        passed=not failures,
        failures=failures,
        tokens_used=tokens_used,
    )


@dataclass
class SuiteReport:
    """Aggregated results over a suite run."""

    results: list

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def pass_rate(self) -> float:
        return (self.passed_count / self.total) if self.total else 0.0

    @property
    def total_tokens(self) -> int:
        return sum(r.tokens_used for r in self.results)

    def failures(self) -> list:
        return [r for r in self.results if not r.passed]

    def render(self) -> str:
        lines = [
            f"Golden suite: {self.passed_count}/{self.total} passed "
            f"({self.pass_rate:.0%})",
            "-" * 60,
        ]
        for result in self.results:
            lines.append(result.render())
        if self.total_tokens:
            lines.append("-" * 60)
            lines.append(f"Total answer-path tokens: {self.total_tokens}")
        if self.failures():
            lines.append("")
            lines.append(
                "Interpretation guidance (Ch. 27): a failing case names its level — "
                "missing facts are grounding failures; missing sources are citation/"
                "retrieval failures; 'answered instead of refusing' is an access-control "
                "or sufficiency failure. Diagnose by level, not by score."
            )
        return "\n".join(lines)


def run_suite(cases: list, pipeline_fn: Callable) -> SuiteReport:
    """Run every case through ``pipeline_fn(case) -> dict``.

    The returned dict must provide ``answer_text``, ``citations``, and
    optionally ``tokens``. This is the ONLY contract between the harness
    and the system under test.
    """
    results = []
    for case in cases:
        output = pipeline_fn(case)
        results.append(
            evaluate_answer(
                answer_text=output["answer_text"],
                citations=output.get("citations", []),
                case=case,
                tokens_used=output.get("tokens", 0),
            )
        )
    return SuiteReport(results=results)


def ablate(
    cases: list,
    baseline_fn: Callable,
    ablations: dict,
) -> dict:
    """Compare the baseline against named variant pipelines (Chapter 28).

    ``ablations`` maps a name (e.g. "no-diversity") to a pipeline_fn.
    Returns {name: SuiteReport} including the baseline under "baseline".
    Hold everything constant except the ablated component; report the
    delta cases explicitly rather than trusting aggregate rates alone.
    """
    reports = {"baseline": run_suite(cases, baseline_fn)}
    for name, fn in ablations.items():
        reports[name] = run_suite(cases, fn)
    return reports

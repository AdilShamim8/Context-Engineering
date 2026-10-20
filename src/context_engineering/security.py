"""Security layer: trust enforcement, injection screening, redaction (Chapter 24).

What this module is: a set of **detection aids and rendering aids** that make
the trust boundary visible and enforceable in code:

- ``screen_untrusted``: heuristic pattern screening of retrieved/tool content
  for classic injection and exfiltration markers, plus obfuscation signals
  (zero-width characters). Returns structured findings — it NEVER decides
  alone; callers apply policy (block, label, escalate).
- ``wrap_untrusted``: delimit and label untrusted blocks so nothing downstream
  can mistake data for instructions.
- ``redact``: log-safe transformation (credentials, tokens, emails) — the
  Chapter 29 rule that traces are redacted by default.

What this module is NOT: a security boundary. Heuristics can be evaded by
phrasing; the actual protections this curriculum relies on are architectural
and live elsewhere: access filtering BEFORE ranking (provenance.py), the
guarded tool path (tools.py), bounded outputs, and the layered policies of
Chapter 24. Any claim that screening makes injected content "safe" is a bug
in either code or documentation — report it (see SECURITY.md).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# -- Detection patterns -------------------------------------------------------

INJECTION_PATTERNS: tuple = (
    ("instruction_override_ignore", "high",
     re.compile(r"ignore\s+(?:all\s+)?(?:previous|prior|above)\s+(?:instructions?|prompts?|rules?)", re.I)),
    ("instruction_override_disregard", "high",
     re.compile(r"disregard\s+(?:any|all|the)?\s*\w{0,30}\s*instructions", re.I)),
    ("admin_mode", "high",
     re.compile(r"\b(?:administrative|admin)\s+mode\b", re.I)),
    ("reveal_system_prompt", "high",
     re.compile(r"reveal\s+(?:your\s+)?(?:system\s+)?prompt", re.I)),
    ("reveal_restricted", "high",
     re.compile(r"reveal\s+(?:the\s+)?(?:contents?\s+of\s+)?restricted\s+documents?", re.I)),
    ("credential_exfiltration", "high",
     re.compile(
         r"(?:\b(?:api\s*keys?|passwords?|secrets?|tokens?|credentials?)\b[^.]{0,30}?"
         r"(?:print|reveal|show|list|send|output|exfiltrat\w*)"
         r"|\b(?:print|reveal|show|list|send|output|exfiltrat\w*)\b[^.]{0,30}?"
         r"\b(?:api\s*keys?|passwords?|secrets?|tokens?|credentials?))",
         re.I)),
    ("policy_falsification", "high",
     re.compile(r"(?:tell|say|state)\s+(?:the\s+)?user\s+that\s+(?:all\s+)?(?:policies?|rules?)\s+(?:now\s+)?(?:allow|permit)", re.I)),
)

ZERO_WIDTH_CHARS = ("\u200b", "\u200c", "\u200d", "\u2060", "\ufeff")

CREDENTIAL_RE = re.compile(r"ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9._-]{20,}")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

REDACTIONS: tuple = (
    (CREDENTIAL_RE, "[REDACTED:credential]"),
    (EMAIL_RE, "[REDACTED:email]"),
)


@dataclass
class Finding:
    """One screening result. Detection aid, not verdict."""

    rule: str
    severity: str  # "high" | "medium"
    excerpt: str   # short, safe-to-log snippet (never the full payload)
    index: int     # character offset in the screened text


def screen_untrusted(text: str) -> list:
    """Heuristically screen untrusted content. Returns findings.

    Severity guide: "high" findings are instruction-override or
    exfiltration shapes — under the default policy they block or escalate.
    "medium" findings (obfuscation signals) do not prove anything by
    themselves but justify closer inspection or stricter downstream
    treatment.
    """
    findings: list = []
    for rule, severity, pattern in INJECTION_PATTERNS:
        match = pattern.search(text)
        if match:
            findings.append(
                Finding(rule=rule, severity=severity,
                        excerpt=match.group(0)[:60], index=match.start())
            )
    for char in ZERO_WIDTH_CHARS:
        index = text.find(char)
        if index != -1:
            findings.append(
                Finding(rule="zero_width_character", severity="medium",
                        excerpt=repr(char), index=index)
            )
            break
    return findings


def has_high_severity(findings: list) -> bool:
    return any(f.severity == "high" for f in findings)


class SecurityScreeningError(ValueError):
    """Raised by policy enforcement when high-severity findings must block."""


def enforce_no_high_severity(findings: list, context_label: str = "") -> None:
    """Policy hook: raise if any high-severity finding is present.

    This is the explicit, testable place where a team's blocking policy
    lives — not buried inside a prompt string.
    """
    if has_high_severity(findings):
        rules = sorted({f.rule for f in findings if f.severity == "high"})
        raise SecurityScreeningError(
            f"untrusted content blocked by screening policy{f' ({context_label})' if context_label else ''}: "
            f"rules triggered: {', '.join(rules)}"
        )


def wrap_untrusted(text: str, label: str = "retrieved content") -> str:
    """Delimit and label an untrusted block.

    The wrapper makes three things true at once: the content is visibly
    data (never instructions), its origin is stated, and downstream
    processors (and models) can find the boundary programmatically.
    Rendering used by assembly.py: `<<<UNTRUSTED ... >>>`.
    """
    return f"<<<UNTRUSTED ({label})\n{text}\n>>>"


def redact(text: str) -> str:
    """Apply log-safe redactions (credentials, emails). Use on ALL traces."""
    for pattern, replacement in REDACTIONS:
        text = pattern.sub(replacement, text)
    return text


def redact_findings(findings: list) -> list:
    """Redact finding excerpts before logging them."""
    return [Finding(rule=f.rule, severity=f.severity,
                     excerpt=redact(f.excerpt), index=f.index) for f in findings]

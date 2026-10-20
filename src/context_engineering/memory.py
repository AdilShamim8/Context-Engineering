"""Persistent memory engineering (Chapter 18).

A MemoryStore is deliberately NOT a database demo: it exists to make the
Chapter 18 policy questions inspectable and testable:

- What kinds of memory exist (facts, preferences, episodic, task notes)?
- Where does a memory come from (user-stated vs. inferred)?  Inferred
  memories carry their provenance — and a responsibility to be auditable.
- When do memories expire, get superseded, or get deleted?
- What happens when memories conflict?  (Flag; never silently resolve.)
- Who may read a memory?  (Access levels, enforced at retrieval.)

Every mutating operation writes an audit event. A memory system without
an audit trail is unauditable in exactly the way Chapter 26 forbids.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone

from .provenance import ACCESS_UNKNOWN, AccessPolicy

WORD_RE = re.compile(r"[a-z0-9']+")
NUMBER_RE = re.compile(r"\b\d+(?:[.,]\d+)?\b")

MEMORY_KINDS = ("fact", "preference", "episodic", "task_note")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class MemoryRecord:
    """One memory item with provenance and lifecycle metadata."""

    record_id: str
    content: str
    kind: str  # one of MEMORY_KINDS
    source: str = "user-stated"  # or "inferred"
    created_at: str = ""
    updated_at: str = ""
    ttl_days: int | None = None   # None = no expiry
    access: str = "internal"
    supersedes: str = ""          # record_id this one replaces
    confidence: float = 1.0       # provenance honesty for inferred memories

    def __post_init__(self):
        if self.kind not in MEMORY_KINDS:
            raise ValueError(f"kind must be one of {MEMORY_KINDS}, got {self.kind!r}")
        now = _now_iso()
        self.created_at = self.created_at or now
        self.updated_at = self.updated_at or now

    def age_days(self, today: date | None = None) -> int:
        try:
            created = datetime.fromisoformat(self.created_at).date()
        except (ValueError, TypeError):
            return 0
        return (today or date.today() - created).days if not today else (today - created).days

    def expired(self, today: date | None = None) -> bool:
        if self.ttl_days is None:
            return False
        return self.age_days(today) > self.ttl_days


class MemoryStore:
    """A small, auditable, access-filtered memory store."""

    def __init__(self) -> None:
        self.records: dict = {}
        self.audit: list = []

    # -- mutation ---------------------------------------------------------

    def upsert(self, record: MemoryRecord) -> dict:
        """Insert or replace a record; return a dict with detected conflicts.

        Conflicts are FLAGGED, never silently resolved: an overlapping memory
        with a different number is the classic "salary band said X, now says
        Y" situation — callers must decide (supersede, keep both labeled, or
        refuse), and the audit trail records the decision they made.
        """
        conflicts = self.detect_conflicts(record)
        replaced = None
        if record.record_id in self.records:
            replaced = self.records[record.record_id]
        self.records[record.record_id] = record
        self.audit.append(
            {
                "op": "replace" if replaced else "insert",
                "record_id": record.record_id,
                "at": _now_iso(),
                "conflicts": [c["other_id"] for c in conflicts],
            }
        )
        return {"record_id": record.record_id, "conflicts": conflicts, "replaced": replaced is not None}

    def detect_conflicts(self, record: MemoryRecord) -> list:
        """Overlapping existing memories that say something different."""
        new_words = set(WORD_RE.findall(record.content.lower()))
        new_numbers = set(NUMBER_RE.findall(record.content))
        conflicts = []
        for other in self.records.values():
            if other.record_id == record.record_id:
                continue
            other_words = set(WORD_RE.findall(other.content.lower()))
            union = new_words | other_words
            if not union:
                continue
            overlap = len(new_words & other_words) / len(union)
            if overlap >= 0.6 and other.content.strip().lower() != record.content.strip().lower():
                other_numbers = set(NUMBER_RE.findall(other.content))
                reason = (
                    "numeric_mismatch" if (new_numbers and new_numbers != other_numbers)
                    else "overlapping_content_differs"
                )
                conflicts.append({"other_id": other.record_id, "reason": reason})
        return conflicts

    def delete(self, record_id: str, reason: str = "user request") -> bool:
        existed = self.records.pop(record_id, None) is not None
        self.audit.append({"op": "delete", "record_id": record_id, "reason": reason, "at": _now_iso()})
        return existed

    def delete_all(self, reason: str = "user request") -> int:
        count = len(self.records)
        self.records.clear()
        self.audit.append({"op": "delete_all", "count": count, "reason": reason, "at": _now_iso()})
        return count

    def purge_expired(self, today: date | None = None) -> list:
        expired_ids = [rid for rid, rec in self.records.items() if rec.expired(today)]
        for rid in expired_ids:
            del self.records[rid]
        if expired_ids:
            self.audit.append({"op": "purge_expired", "record_ids": expired_ids, "at": _now_iso()})
        return expired_ids

    # -- retrieval ---------------------------------------------------------

    def retrieve(self, query: str, k: int = 4, access_policy: AccessPolicy | None = None) -> list:
        """Keyword-scored retrieval over live (non-expired) records.

        Access filtering applies BEFORE scoring (the Chapter 9 rule, again).
        Expired records are invisible here even before an explicit purge.
        """
        query_words = set(WORD_RE.findall(query.lower()))
        today = date.today()
        candidates: list = []
        for record in self.records.values():
            if record.expired(today):
                continue
            if access_policy is not None:
                level = getattr(record, "access", ACCESS_UNKNOWN) or ACCESS_UNKNOWN
                if not access_policy.allows(level):
                    continue
            content_words = set(WORD_RE.findall(record.content.lower()))
            score = len(query_words & content_words) / max(len(query_words), 1)
            if score > 0:
                candidates.append((score, record))
        candidates.sort(key=lambda pair: (-pair[0], pair[1].record_id))
        return [record for _, record in candidates[:k]]

    # -- persistence ---------------------------------------------------------

    def to_state(self) -> dict:
        return {
            "records": [asdict(r) for r in self.records.values()],
            "audit": list(self.audit),
        }

    @classmethod
    def from_state(cls, state: dict) -> "MemoryStore":
        store = cls()
        for rec_state in state["records"]:
            record = MemoryRecord(**rec_state)
            store.records[record.record_id] = record
        store.audit = list(state["audit"])
        return store

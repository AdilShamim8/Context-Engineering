"""Provenance, freshness, and access-aware retrieval (Chapter 9).

Three policy families, all enforced BEFORE anything reaches a model
context:

- AccessPolicy — who may see which access classes. Fails CLOSED: chunks
  whose access level is unknown are excluded, because "we don't know who
  may read this" is not a permission.
- FreshnessPolicy — what "too old" means for a source, and whether stale
  sources are excluded, labeled, or merely tolerated.
- Version selection — when several versions of one document exist, the
  current version wins; superseded versions must not silently compete.

The recurring lesson of Chapter 9: none of these can be implemented as a
prompt instruction ("please ignore old documents"). They are pipeline
stages with tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .retrieval import Chunk

#: Access class assigned when a chunk carries no access information at all.
#: Policies do not include it by default → unknown means excluded (fail closed).
ACCESS_UNKNOWN = "unknown"


def _field(item, name, default=None):
    if isinstance(item, dict):
        return item.get(name, default)
    return getattr(item, name, default)


def _access_of(chunk) -> str:
    source = _field(chunk, "source", None)
    if source is not None:
        access = _field(source, "access", "")
        if access:
            return access
    metadata = _field(chunk, "metadata", None) or {}
    return metadata.get("access", ACCESS_UNKNOWN)


@dataclass(frozen=True)
class AccessPolicy:
    """The set of access classes a request (user/tenant) may see."""

    allowed: frozenset

    @classmethod
    def from_levels(cls, *levels: str) -> "AccessPolicy":
        return cls(allowed=frozenset(levels))

    def allows(self, access_level: str) -> bool:
        return access_level in self.allowed

    def filter(self, chunks) -> list:
        """Keep only chunks whose access level is explicitly allowed."""
        return [c for c in chunks if self.allows(_access_of(c))]

    def as_predicate(self):
        """Return a chunk -> bool predicate for LexicalIndex.search."""

        def predicate(chunk) -> bool:
            return self.allows(_access_of(chunk))

        return predicate


@dataclass
class FreshnessVerdict:
    ok: bool          # may this source be used?
    stale: bool       # is it old by policy?
    age_days: int
    reason: str = ""


class FreshnessPolicy:
    """Decide whether a source's age makes it unusable or suspect.

    ``on_stale`` actions:
      - "exclude": stale sources are dropped from candidates entirely.
      - "label":   stale sources stay, but downstream assembly adds a
                   stale marker (the failure becomes visible, not silent).
      - "allow":  no action (for corpora where age is irrelevant).
    """

    def __init__(self, max_age_days=None, on_stale: str = "label") -> None:
        if on_stale not in ("exclude", "label", "allow"):
            raise ValueError(f"unknown on_stale action: {on_stale!r}")
        self.max_age_days = max_age_days
        self.on_stale = on_stale

    def verdict(self, source, today: date | None = None) -> FreshnessVerdict:
        today = today or date.today()
        effective = _field(source, "effective_date", "") or ""
        if not effective:
            return FreshnessVerdict(
                ok=True, stale=False, age_days=-1,
                reason="no effective date on source; freshness unassessed",
            )
        try:
            eff_date = date.fromisoformat(str(effective)[:10])
        except ValueError:
            return FreshnessVerdict(
                ok=True, stale=False, age_days=-1,
                reason=f"unparseable effective date {effective!r}",
            )
        age_days = (today - eff_date).days
        if self.max_age_days is not None and age_days > self.max_age_days:
            reason = f"{age_days} days old (max {self.max_age_days})"
            if self.on_stale == "exclude":
                return FreshnessVerdict(ok=False, stale=True, age_days=age_days, reason=reason)
            if self.on_stale == "label":
                return FreshnessVerdict(ok=True, stale=True, age_days=age_days, reason=reason)
            return FreshnessVerdict(ok=True, stale=True, age_days=age_days, reason=reason + " (allowed by policy)")
        return FreshnessVerdict(ok=True, stale=False, age_days=age_days, reason="")


def _version_key(item):
    version = str(_field(item, "version", "") or "")
    effective = str(_field(item, "effective_date", "") or "")
    numeric = int(version) if version.isdigit() else 0
    return (numeric, effective)


def select_current_versions(items) -> list:
    """From a list of versioned items, keep only the newest per source_id.

    Works for dicts and objects (attribute or mapping access). Superseded
    versions are dropped — the default conflict resolution policy. Other
    policies (keep-and-label) are discussed in Chapter 9 and can be built
    on group_by_source below.
    """
    latest: dict = {}
    for item in items:
        sid = _field(item, "source_id", None)
        if sid is None and isinstance(item, dict):
            sid = item.get("id")
        if sid is None:
            sid = _field(item, "source_id", "")
        if sid not in latest or _version_key(item) > _version_key(latest[sid]):
            latest[sid] = item
    return list(latest.values())


def group_by_source(items) -> dict:
    """Group items by source_id — the starting point for conflict labeling."""
    grouped: dict = {}
    for item in items:
        sid = _field(item, "source_id", None)
        if sid is None and isinstance(item, dict):
            sid = item.get("id")
        grouped.setdefault(sid, []).append(item)
    return grouped

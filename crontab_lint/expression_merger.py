"""Merge multiple crontab expressions into a minimal equivalent set."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse, ParseError
from .explainer import explain


@dataclass
class MergeEntry:
    original: List[str]
    merged: str
    explanation: Optional[str]
    is_valid: bool
    error: Optional[str] = None


@dataclass
class MergeResult:
    entries: List[MergeEntry] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.entries)

    @property
    def valid_count(self) -> int:
        return sum(1 for e in self.entries if e.is_valid)


def _fields(expr: str) -> Optional[List[str]]:
    try:
        parsed = parse(expr)
        return [
            parsed.minute,
            parsed.hour,
            parsed.day_of_month,
            parsed.month,
            parsed.day_of_week,
        ]
    except ParseError:
        return None


def _try_merge_two(a: str, b: str) -> Optional[str]:
    """Attempt to merge two expressions that differ in exactly one field."""
    fa = _fields(a)
    fb = _fields(b)
    if fa is None or fb is None:
        return None
    diffs = [(i, fa[i], fb[i]) for i in range(5) if fa[i] != fb[i]]
    if len(diffs) != 1:
        return None
    idx, va, vb = diffs[0]
    merged_fields = list(fa)
    merged_fields[idx] = f"{va},{vb}"
    return " ".join(merged_fields)


def merge(expressions: List[str]) -> MergeResult:
    """Group and merge expressions that share all fields except one."""
    result = MergeResult()
    valid = []
    for raw in expressions:
        line = raw.strip()
        if not line or line.startswith("#"):
            result.skipped.append(raw)
            continue
        if _fields(line) is None:
            result.skipped.append(raw)
            continue
        valid.append(line)

    used = [False] * len(valid)
    for i in range(len(valid)):
        if used[i]:
            continue
        group = [valid[i]]
        current = valid[i]
        for j in range(i + 1, len(valid)):
            if used[j]:
                continue
            merged = _try_merge_two(current, valid[j])
            if merged is not None:
                group.append(valid[j])
                current = merged
                used[j] = True
        used[i] = True
        try:
            parsed = parse(current)
            exp = explain(parsed)
            entry = MergeEntry(
                original=group,
                merged=current,
                explanation=exp,
                is_valid=True,
            )
        except ParseError as exc:
            entry = MergeEntry(
                original=group,
                merged=current,
                explanation=None,
                is_valid=False,
                error=str(exc),
            )
        result.entries.append(entry)
    return result

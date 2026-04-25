"""Auto-tag cron expressions based on their frequency and structure."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from crontab_lint.parser import parse, ParseError
from crontab_lint.frequency_analyzer import analyze


@dataclass
class TaggingResult:
    expression: str
    tags: List[str] = field(default_factory=list)
    is_valid: bool = True
    error: str | None = None

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags


_SPECIAL_STRING_TAGS = {
    "@yearly": ["yearly", "rare"],
    "@annually": ["yearly", "rare"],
    "@monthly": ["monthly", "rare"],
    "@weekly": ["weekly", "rare"],
    "@daily": ["daily", "scheduled"],
    "@midnight": ["daily", "scheduled"],
    "@hourly": ["hourly", "frequent"],
    "@reboot": ["reboot", "system"],
}


def _tags_from_fields(expr) -> List[str]:
    """Derive structural tags from a parsed CronExpression."""
    tags: List[str] = []
    analysis = analyze(expr.raw)
    if analysis.is_valid:
        cat = analysis.category
        if cat:
            tags.append(cat.lower().replace(" ", "_"))

    # Structural tags
    fields = [expr.minute, expr.hour, expr.day_of_month, expr.month, expr.day_of_week]
    if all(f == "*" for f in fields):
        tags.append("every_minute")
    if any("/" in f for f in fields):
        tags.append("step")
    if any("-" in f for f in fields):
        tags.append("range")
    if any("," in f for f in fields):
        tags.append("list")
    return tags


def auto_tag(expression: str) -> TaggingResult:
    """Return a TaggingResult with auto-generated tags for *expression*."""
    stripped = expression.strip()
    lower = stripped.lower()
    if lower in _SPECIAL_STRING_TAGS:
        return TaggingResult(
            expression=stripped,
            tags=list(_SPECIAL_STRING_TAGS[lower]),
            is_valid=True,
        )
    try:
        expr = parse(stripped)
    except ParseError as exc:
        return TaggingResult(expression=stripped, is_valid=False, error=str(exc))

    tags = _tags_from_fields(expr)
    # Deduplicate while preserving order
    seen: List[str] = []
    for t in tags:
        if t not in seen:
            seen.append(t)
    return TaggingResult(expression=stripped, tags=seen, is_valid=True)

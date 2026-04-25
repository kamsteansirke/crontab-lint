"""Sanitize crontab expressions by stripping noise and normalizing whitespace."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from crontab_lint.parser import parse, ParseError


@dataclass
class SanitizeResult:
    original: str
    sanitized: str
    changed: bool
    valid: bool
    error: Optional[str] = None

    def ok(self) -> bool:
        return self.valid


def _strip_inline_comment(expression: str) -> str:
    """Remove trailing inline comments (# ...) from an expression."""
    # Only strip if the # is preceded by whitespace to avoid breaking fields
    parts = expression.split("#", 1)
    if len(parts) == 2 and parts[0].rstrip() != parts[0]:
        return parts[0].rstrip()
    # Also handle case where # comes after at least one space
    idx = expression.find(" #")
    if idx != -1:
        return expression[:idx].rstrip()
    return expression


def _collapse_whitespace(expression: str) -> str:
    """Collapse multiple spaces/tabs into a single space."""
    return " ".join(expression.split())


def _remove_trailing_semicolon(expression: str) -> str:
    return expression.rstrip(";")


def sanitize(expression: str) -> SanitizeResult:
    """Sanitize a single crontab expression string."""
    original = expression

    result = expression.strip()
    result = _strip_inline_comment(result)
    result = _remove_trailing_semicolon(result)
    result = _collapse_whitespace(result)

    changed = result != original

    try:
        parse(result)
        return SanitizeResult(
            original=original,
            sanitized=result,
            changed=changed,
            valid=True,
        )
    except ParseError as exc:
        return SanitizeResult(
            original=original,
            sanitized=result,
            changed=changed,
            valid=False,
            error=str(exc),
        )


def sanitize_many(expressions: list[str]) -> list[SanitizeResult]:
    """Sanitize a list of crontab expression strings."""
    return [sanitize(expr) for expr in expressions]

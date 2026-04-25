"""Aggregated validation report for a collection of crontab expressions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse, ParseError
from .explainer import explain


@dataclass
class ValidationEntry:
    expression: str
    valid: bool
    explanation: Optional[str] = None
    error: Optional[str] = None


@dataclass
class ValidationReport:
    entries: List[ValidationEntry] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.entries)

    @property
    def valid_count(self) -> int:
        return sum(1 for e in self.entries if e.valid)

    @property
    def invalid_count(self) -> int:
        return sum(1 for e in self.entries if not e.valid)

    @property
    def all_valid(self) -> bool:
        return self.invalid_count == 0


def validate_expressions(expressions: List[str]) -> ValidationReport:
    """Validate a list of crontab expression strings and return a report."""
    entries: List[ValidationEntry] = []
    for raw in expressions:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            parsed = parse(line)
            explanation = explain(parsed)
            entries.append(ValidationEntry(
                expression=line,
                valid=True,
                explanation=explanation,
            ))
        except ParseError as exc:
            entries.append(ValidationEntry(
                expression=line,
                valid=False,
                error=str(exc),
            ))
    return ValidationReport(entries=entries)

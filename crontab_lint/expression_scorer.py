"""Score crontab expressions by readability and best-practice metrics."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .parser import parse, ParseError


@dataclass
class ScoreDetail:
    category: str
    message: str
    points: int  # positive = bonus, negative = penalty


@dataclass
class ExpressionScore:
    expression: str
    total: int
    max_score: int
    details: List[ScoreDetail] = field(default_factory=list)
    valid: bool = True
    error: str = ""

    @property
    def grade(self) -> str:
        if not self.valid:
            return "F"
        pct = self.total / self.max_score if self.max_score else 0
        if pct >= 0.9:
            return "A"
        if pct >= 0.75:
            return "B"
        if pct >= 0.6:
            return "C"
        if pct >= 0.4:
            return "D"
        return "F"


_MAX_SCORE = 100


def score(expression: str) -> ExpressionScore:
    """Return a scored breakdown for *expression*."""
    details: List[ScoreDetail] = []

    try:
        expr = parse(expression)
    except ParseError as exc:
        return ExpressionScore(
            expression=expression,
            total=0,
            max_score=_MAX_SCORE,
            valid=False,
            error=str(exc),
        )

    total = 0

    # Base validity bonus
    details.append(ScoreDetail("validity", "Parses successfully", 40))
    total += 40

    # Wildcard overuse penalty
    fields = [expr.minute, expr.hour, expr.day_of_month, expr.month, expr.day_of_week]
    wildcard_count = sum(1 for f in fields if f == "*")
    if wildcard_count == 5:
        details.append(ScoreDetail("specificity", "All fields are wildcards (runs every minute)", -20))
        total -= 20
    elif wildcard_count <= 2:
        details.append(ScoreDetail("specificity", "Good field specificity", 20))
        total += 20
    else:
        details.append(ScoreDetail("specificity", f"{wildcard_count} wildcard fields — consider being more specific", 5))
        total += 5

    # Step value bonus (indicates intentional scheduling)
    has_step = any("/" in f for f in fields)
    if has_step:
        details.append(ScoreDetail("readability", "Uses step values — clear interval intent", 10))
        total += 10

    # Named special string bonus
    specials = {"@yearly", "@annually", "@monthly", "@weekly", "@daily", "@midnight", "@hourly"}
    if expression.strip().split()[0] in specials:
        details.append(ScoreDetail("readability", "Uses a named special string — very readable", 20))
        total += 20
    else:
        details.append(ScoreDetail("readability", "Standard five-field expression", 10))
        total += 10

    # Clamp to [0, _MAX_SCORE]
    total = max(0, min(_MAX_SCORE, total))

    return ExpressionScore(
        expression=expression,
        total=total,
        max_score=_MAX_SCORE,
        details=details,
    )

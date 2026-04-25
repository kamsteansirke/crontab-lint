"""Assess risk level of crontab expressions based on frequency, complexity, and overlap potential."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from crontab_lint.parser import parse, ParseError
from crontab_lint.frequency_analyzer import analyze


RISK_LOW = "low"
RISK_MEDIUM = "medium"
RISK_HIGH = "high"
RISK_CRITICAL = "critical"


@dataclass
class RiskFactor:
    name: str
    description: str
    severity: str  # low / medium / high / critical


@dataclass
class RiskAssessment:
    expression: str
    is_valid: bool
    risk_level: str
    risk_score: int  # 0-100
    factors: List[RiskFactor] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def has_risks(self) -> bool:
        return bool(self.factors)


_SEVERITY_WEIGHT = {RISK_LOW: 5, RISK_MEDIUM: 20, RISK_HIGH: 40, RISK_CRITICAL: 60}


def _level_from_score(score: int) -> str:
    if score >= 60:
        return RISK_CRITICAL
    if score >= 35:
        return RISK_HIGH
    if score >= 15:
        return RISK_MEDIUM
    return RISK_LOW


def assess(expression: str) -> RiskAssessment:
    """Return a RiskAssessment for the given cron expression string."""
    try:
        parse(expression)
    except ParseError as exc:
        return RiskAssessment(
            expression=expression,
            is_valid=False,
            risk_level=RISK_HIGH,
            risk_score=50,
            error=str(exc),
        )

    factors: List[RiskFactor] = []

    fa = analyze(expression)
    if fa.is_valid:
        if fa.runs_per_day is not None:
            if fa.runs_per_day >= 1440:
                factors.append(RiskFactor(
                    "every_minute",
                    "Runs every minute — very high system load.",
                    RISK_CRITICAL,
                ))
            elif fa.runs_per_day >= 60:
                factors.append(RiskFactor(
                    "high_frequency",
                    f"Runs {fa.runs_per_day} times per day — high frequency.",
                    RISK_HIGH,
                ))
            elif fa.runs_per_day >= 24:
                factors.append(RiskFactor(
                    "medium_frequency",
                    f"Runs {fa.runs_per_day} times per day.",
                    RISK_MEDIUM,
                ))

    raw = expression.strip()
    if "*/1" in raw:
        factors.append(RiskFactor(
            "redundant_step",
            "Step of 1 is redundant and may indicate a misconfiguration.",
            RISK_LOW,
        ))

    if raw.startswith("@reboot"):
        factors.append(RiskFactor(
            "reboot_trigger",
            "Runs on every system reboot — ensure idempotency.",
            RISK_MEDIUM,
        ))

    score = min(100, sum(_SEVERITY_WEIGHT[f.severity] for f in factors))
    return RiskAssessment(
        expression=expression,
        is_valid=True,
        risk_level=_level_from_score(score),
        risk_score=score,
        factors=factors,
    )


def assess_many(expressions: List[str]) -> List[RiskAssessment]:
    return [assess(e) for e in expressions]

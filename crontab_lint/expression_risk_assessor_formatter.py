"""Formatters for RiskAssessment results."""
from __future__ import annotations
from typing import List
from crontab_lint.expression_risk_assessor import RiskAssessment, RISK_CRITICAL, RISK_HIGH

_ICONS = {
    "low": "✅",
    "medium": "⚠️",
    "high": "🔴",
    "critical": "💀",
}

_SEV_ICONS = {
    "low": "·",
    "medium": "!",
    "high": "!!",
    "critical": "!!!",
}


def format_assessment(assessment: RiskAssessment, index: int | None = None) -> str:
    lines: List[str] = []
    prefix = f"[{index}] " if index is not None else ""
    icon = _ICONS.get(assessment.risk_level, "?")

    if not assessment.is_valid:
        lines.append(f"{prefix}{icon} INVALID  {assessment.expression}")
        lines.append(f"   Error   : {assessment.error}")
        lines.append(f"   Risk    : {assessment.risk_level.upper()} (score {assessment.risk_score})")
        return "\n".join(lines)

    lines.append(f"{prefix}{icon} {assessment.expression}")
    lines.append(f"   Risk    : {assessment.risk_level.upper()} (score {assessment.risk_score}/100)")

    if assessment.factors:
        lines.append("   Factors :")
        for factor in assessment.factors:
            sev = _SEV_ICONS.get(factor.severity, "?")
            lines.append(f"     [{sev}] {factor.name}: {factor.description}")
    else:
        lines.append("   Factors : none")

    return "\n".join(lines)


def format_assessments(assessments: List[RiskAssessment]) -> str:
    if not assessments:
        return "No expressions to assess."
    parts = [
        format_assessment(a, index=i + 1) for i, a in enumerate(assessments)
    ]
    return "\n\n".join(parts)


def format_summary(assessments: List[RiskAssessment]) -> str:
    total = len(assessments)
    if total == 0:
        return "Summary: 0 expressions assessed."
    invalid = sum(1 for a in assessments if not a.is_valid)
    critical = sum(1 for a in assessments if a.risk_level == RISK_CRITICAL)
    high = sum(1 for a in assessments if a.risk_level == RISK_HIGH)
    lines = [
        f"Summary: {total} expression(s) assessed.",
        f"  Invalid : {invalid}",
        f"  Critical: {critical}",
        f"  High    : {high}",
        f"  Other   : {total - invalid - critical - high}",
    ]
    return "\n".join(lines)

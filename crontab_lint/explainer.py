"""Human-readable explanations for crontab expressions."""

from .parser import CronExpression

ORDINALS = {
    1: "1st", 2: "2nd", 3: "3rd",
    **{i: f"{i}th" for i in range(4, 32)},
}

DAYS_OF_WEEK = {
    0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday",
    4: "Thursday", 5: "Friday", 6: "Saturday",
}

MONTHS = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December",
}


def _explain_field(value: str, kind: str) -> str:
    if = value.split(",")
        if kind == "day of week":
            parts = [DAYS_OF_WEEK.n    if "/" in value:
        base, step = value.split("/")
        return f"every {step} {kind}s"
    if "-" in value:
        start, end = value.split("-")
        return f"{kind} {start} through {end}"
    if kind == "day of week":
        return DAYS_OF_WEEK.get(int(value), value)
    if kind == "month":
        return MONTHS.get(int(value), value)
    if kind == "day of month":
        return f"the {ORDINALS.get(int(value), value)} day"
    return f"at {value}"


def explain(expr: CronExpression) -> str:
    """Return a human-readable explanation of a CronExpression."""
    if expr.special:
        mapping = {
            "@yearly": "Once a year, at midnight on January 1st",
            "@annually": "Once a year, at midnight on January 1st",
            "@monthly": "Once a month, at midnight on the 1st",
            "@weekly": "Once a week, at midnight on Sunday",
            "@daily": "Once a day, at midnight",
            "@midnight": "Once a day, at midnight",
            "@hourly": "Once an hour, at the start of the hour",
            "@reboot": "At system reboot",
        }
        return mapping.get(expr.special, f"Special: {expr.special}")

    minute = _explain_field(expr.minute, "minute")
    hour = _explain_field(expr.hour, "hour")
    dom = _explain_field(expr.day_of_month, "day of month")
    month = _explain_field(expr.month, "month")
    dow = _explain_field(expr.day_of_week, "day of week")

    parts = []
    if expr.minute != "*" or expr.hour != "*":
        parts.append(f"at {minute} past {hour}")
    else:
        parts.append("every minute of every hour")

    if expr.day_of_month != "*":
        parts.append(f"on {dom}")
    if expr.month != "*":
        parts.append(f"in {month}")
    if expr.day_of_week != "*":
        parts.append(f"on {dow}")

    return ", ".join(parts)

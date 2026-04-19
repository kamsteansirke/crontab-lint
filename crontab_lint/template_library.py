"""Built-in crontab expression templates."""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Template:
    name: str
    expression: str
    description: str
    tags: List[str] = field(default_factory=list)


BUILTIN_TEMPLATES: List[Template] = [
    Template("every-minute", "* * * * *", "Runs every minute", ["frequent"]),
    Template("every-hour", "0 * * * *", "Runs at the start of every hour", ["hourly"]),
    Template("daily-midnight", "0 0 * * *", "Runs daily at midnight", ["daily"]),
    Template("daily-noon", "0 12 * * *", "Runs daily at noon", ["daily"]),
    Template("weekly-sunday", "0 0 * * 0", "Runs every Sunday at midnight", ["weekly"]),
    Template("monthly-first", "0 0 1 * *", "Runs on the 1st of every month at midnight", ["monthly"]),
    Template("weekdays-9am", "0 9 * * 1-5", "Runs at 9am on weekdays", ["weekdays", "business"]),
    Template("every-6-hours", "0 */6 * * *", "Runs every 6 hours", ["frequent"]),
    Template("every-15-minutes", "*/15 * * * *", "Runs every 15 minutes", ["frequent"]),
    Template("yearly", "0 0 1 1 *", "Runs once a year on Jan 1st", ["yearly"]),
]


def list_templates() -> List[Template]:
    return list(BUILTIN_TEMPLATES)


def find_by_name(name: str) -> Optional[Template]:
    for t in BUILTIN_TEMPLATES:
        if t.name == name:
            return t
    return None


def find_by_tag(tag: str) -> List[Template]:
    return [t for t in BUILTIN_TEMPLATES if tag in t.tags]


def search(query: str) -> List[Template]:
    q = query.lower()
    return [
        t for t in BUILTIN_TEMPLATES
        if q in t.name.lower() or q in t.description.lower() or any(q in tag for tag in t.tags)
    ]

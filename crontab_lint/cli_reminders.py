"""CLI for managing cron expression reminders."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .reminder import Reminder, ReminderStore
from .reminder_formatter import format_reminders, format_summary

DEFAULT_PATH = Path.home() / ".crontab_lint" / "reminders.json"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crontab-reminders",
        description="Manage reminders attached to cron expressions.",
    )
    sub = p.add_subparsers(dest="command")

    add_p = sub.add_parser("add", help="Add a reminder")
    add_p.add_argument("expression", help="Cron expression")
    add_p.add_argument("note", help="Reminder note")
    add_p.add_argument("--due", default=None, help="Due date (YYYY-MM-DD)")
    add_p.add_argument("--tags", nargs="*", default=[], help="Optional tags")

    rm_p = sub.add_parser("remove", help="Remove a reminder by note text")
    rm_p.add_argument("note", help="Exact note text to remove")

    sub.add_parser("list", help="List all reminders")
    sub.add_parser("overdue", help="Show overdue reminders")

    for parser in (p, add_p, rm_p):
        parser.add_argument(
            "--file", default=str(DEFAULT_PATH), help="Path to reminders file"
        )
    return p


def run_reminders(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    store_path = Path(getattr(args, "file", str(DEFAULT_PATH)))
    store_path.parent.mkdir(parents=True, exist_ok=True)
    store = ReminderStore(store_path)

    if args.command == "add":
        reminder = Reminder(
            expression=args.expression,
            note=args.note,
            due=args.due,
            tags=args.tags,
        )
        store.add(reminder)
        print(f"Reminder added: {args.note}")

    elif args.command == "remove":
        removed = store.remove(args.note)
        if removed:
            print(f"Removed reminder: {args.note}")
        else:
            print(f"No reminder found with note: {args.note}", file=sys.stderr)
            return 1

    elif args.command == "list":
        reminders = store.all()
        print(format_reminders(reminders))
        if reminders:
            print()
            print(format_summary(reminders))

    elif args.command == "overdue":
        reminders = store.overdue()
        print(format_reminders(reminders))

    return 0


def main() -> None:
    sys.exit(run_reminders())

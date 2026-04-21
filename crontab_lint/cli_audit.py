"""CLI interface for viewing and filtering the audit log."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .audit_log import AuditLog
from .audit_log_formatter import format_audit_log, format_summary

DEFAULT_AUDIT_FILE = Path.home() / ".crontab_lint" / "audit.json"


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the audit subcommand."""
    parser = argparse.ArgumentParser(
        prog="crontab-lint audit",
        description="View and filter the crontab-lint audit log.",
    )
    subparsers = parser.add_subparsers(dest="command")

    # list subcommand
    list_parser = subparsers.add_parser("list", help="List recent audit entries")
    list_parser.add_argument(
        "-n",
        "--limit",
        type=int,
        default=20,
        metavar="N",
        help="Maximum number of entries to show (default: 20)",
    )
    list_parser.add_argument(
        "--action",
        metavar="ACTION",
        help="Filter entries by action (e.g. lint, export, tag)",
    )
    list_parser.add_argument(
        "--file",
        metavar="PATH",
        default=str(DEFAULT_AUDIT_FILE),
        help="Path to audit log file",
    )

    # summary subcommand
    summary_parser = subparsers.add_parser("summary", help="Show audit log summary")
    summary_parser.add_argument(
        "--file",
        metavar="PATH",
        default=str(DEFAULT_AUDIT_FILE),
        help="Path to audit log file",
    )

    # clear subcommand
    clear_parser = subparsers.add_parser("clear", help="Clear the audit log")
    clear_parser.add_argument(
        "--file",
        metavar="PATH",
        default=str(DEFAULT_AUDIT_FILE),
        help="Path to audit log file",
    )
    clear_parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompt",
    )

    return parser


def run_audit(argv: list[str] | None = None) -> int:
    """Run the audit CLI and return an exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    log_path = Path(args.file)
    log = AuditLog(log_path)

    if args.command == "list":
        entries = log.recent(limit=args.limit, action=args.action if args.action else None)
        if not entries:
            print("No audit entries found.")
            return 0
        print(format_audit_log(entries))
        return 0

    if args.command == "summary":
        entries = log.recent(limit=None)
        if not entries:
            print("Audit log is empty.")
            return 0
        print(format_summary(entries))
        return 0

    if args.command == "clear":
        if not args.yes:
            answer = input("Clear the entire audit log? [y/N] ").strip().lower()
            if answer != "y":
                print("Aborted.")
                return 0
        log.clear()
        print(f"Audit log cleared: {log_path}")
        return 0

    parser.print_help()
    return 0


def main() -> None:
    """Entry point for the audit CLI."""
    sys.exit(run_audit())


if __name__ == "__main__":
    main()

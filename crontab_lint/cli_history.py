"""CLI sub-tool for browsing crontab-lint history."""
from __future__ import annotations

import argparse
import sys

from crontab_lint import history as hist_mod


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-history",
        description="Browse or clear crontab-lint expression history.",
    )
    sub = parser.add_subparsers(dest="command")

    show = sub.add_parser("show", help="Show recent history")
    show.add_argument("-n", type=int, default=10, help="Number of entries to show")
    show.add_argument("--file", default=hist_mod.DEFAULT_HISTORY_FILE)

    clr = sub.add_parser("clear", help="Clear history")
    clr.add_argument("--file", default=hist_mod.DEFAULT_HISTORY_FILE)

    return parser


def run_history(args: list[str] | None = None) -> int:
    parser = build_parser()
    ns = parser.parse_args(args)

    if ns.command == "show":
        h = hist_mod.load(ns.file)
        entries = h.recent(ns.n)
        if not entries:
            print("No history found.")
            return 0
        for i, e in enumerate(entries, 1):
            status = "VALID" if e.valid else "INVALID"
            print(f"{i:3}. [{e.timestamp}] {status:7} {e.expression}")
            if e.explanation:
                print(f"       {e.explanation}")
        return 0

    if ns.command == "clear":
        h = hist_mod.load(ns.file)
        h.clear()
        hist_mod.save(h, ns.file)
        print("History cleared.")
        return 0

    parser.print_help()
    return 0


def main() -> None:
    sys.exit(run_history())


if __name__ == "__main__":
    main()

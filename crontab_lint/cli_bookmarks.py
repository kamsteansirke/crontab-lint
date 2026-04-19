"""CLI for managing cron expression bookmarks."""
from __future__ import annotations

import argparse
from pathlib import Path

from crontab_lint import bookmark as bm_mod


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="crontab-bookmarks", description="Manage cron bookmarks")
    sub = parser.add_subparsers(dest="command")

    add_p = sub.add_parser("add", help="Add a bookmark")
    add_p.add_argument("expression", help="Cron expression")
    add_p.add_argument("label", help="Short label")
    add_p.add_argument("--notes", default="", help="Optional notes")

    rm_p = sub.add_parser("remove", help="Remove a bookmark by label")
    rm_p.add_argument("label")

    find_p = sub.add_parser("find", help="Find a bookmark by label")
    find_p.add_argument("label")

    sub.add_parser("list", help="List all bookmarks")
    return parser


def run_bookmarks(args: list[str] | None = None, store_path: Path = bm_mod.DEFAULT_PATH) -> int:
    parser = build_parser()
    ns = parser.parse_args(args)

    if ns.command is None:
        parser.print_help()
        return 0

    store = bm_mod.load(store_path)

    if ns.command == "add":
        entry = store.add(ns.expression, ns.label, ns.notes)
        bm_mod.save(store, store_path)
        print(f"Bookmarked '{entry.label}': {entry.expression}")

    elif ns.command == "remove":
        removed = store.remove(ns.label)
        if removed:
            bm_mod.save(store, store_path)
            print(f"Removed bookmark '{ns.label}'")
        else:
            print(f"No bookmark with label '{ns.label}'")
            return 1

    elif ns.command == "find":
        entry = store.find(ns.label)
        if entry:
            print(f"{entry.label}: {entry.expression}")
            if entry.notes:
                print(f"  Notes: {entry.notes}")
        else:
            print(f"No bookmark with label '{ns.label}'")
            return 1

    elif ns.command == "list":
        entries = store.all()
        if not entries:
            print("No bookmarks saved.")
        for e in entries:
            line = f"  {e.label}: {e.expression}"
            if e.notes:
                line += f" ({e.notes})"
            print(line)

    return 0


def main() -> None:
    raise SystemExit(run_bookmarks())

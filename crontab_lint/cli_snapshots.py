"""CLI for snapshot management."""
from __future__ import annotations
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from crontab_lint.snapshot import Snapshot, SnapshotStore, add, find, remove, compare
from crontab_lint.snapshot_formatter import format_snapshot, format_comparison, format_list

DEFAULT_PATH = Path(".crontab_snapshots.json")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="crontab-snapshots", description="Manage crontab snapshots")
    sub = p.add_subparsers(dest="command")

    save_p = sub.add_parser("save", help="Save a snapshot")
    save_p.add_argument("name")
    save_p.add_argument("expressions", nargs="+")

    show_p = sub.add_parser("show", help="Show a snapshot")
    show_p.add_argument("name")

    cmp_p = sub.add_parser("compare", help="Compare two snapshots")
    cmp_p.add_argument("old")
    cmp_p.add_argument("new")

    sub.add_parser("list", help="List all snapshots")

    del_p = sub.add_parser("delete", help="Delete a snapshot")
    del_p.add_argument("name")

    return p


def run_snapshots(args: list[str] | None = None, store_path: Path = DEFAULT_PATH) -> int:
    parser = build_parser()
    ns = parser.parse_args(args)
    store = SnapshotStore.load(store_path)

    if ns.command == "save":
        ts = datetime.now(timezone.utc).isoformat()
        snap = Snapshot(name=ns.name, expressions=ns.expressions, created_at=ts)
        add(store, snap)
        print(f"Snapshot '{ns.name}' saved with {len(ns.expressions)} expression(s).")

    elif ns.command == "show":
        snap = find(store, ns.name)
        if not snap:
            print(f"Snapshot '{ns.name}' not found.", file=sys.stderr)
            return 1
        print(format_snapshot(snap))

    elif ns.command == "compare":
        old = find(store, ns.old)
        new = find(store, ns.new)
        if not old or not new:
            missing = ns.old if not old else ns.new
            print(f"Snapshot '{missing}' not found.", file=sys.stderr)
            return 1
        diff = compare(old, new)
        print(format_comparison(diff, ns.old, ns.new))

    elif ns.command == "list":
        print(format_list([s.name for s in store.snapshots]))

    elif ns.command == "delete":
        if remove(store, ns.name):
            print(f"Snapshot '{ns.name}' deleted.")
        else:
            print(f"Snapshot '{ns.name}' not found.", file=sys.stderr)
            return 1
    else:
        parser.print_help()

    return 0


def main() -> None:
    sys.exit(run_snapshots())

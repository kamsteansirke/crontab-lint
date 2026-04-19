from crontab_lint.snapshot import Snapshot
from crontab_lint.snapshot_formatter import format_snapshot, format_comparison, format_list


def test_format_snapshot_contains_name():
    s = Snapshot("daily", ["0 0 * * *"])
    out = format_snapshot(s)
    assert "daily" in out


def test_format_snapshot_contains_expressions():
    s = Snapshot("x", ["* * * * *", "0 1 * * *"])
    out = format_snapshot(s)
    assert "* * * * *" in out
    assert "0 1 * * *" in out


def test_format_snapshot_shows_created_at():
    s = Snapshot("x", [], created_at="2024-06-01")
    assert "2024-06-01" in format_snapshot(s)


def test_format_comparison_added():
    diff = {"added": ["0 2 * * *"], "removed": [], "unchanged": []}
    out = format_comparison(diff, "old", "new")
    assert "+" in out
    assert "0 2 * * *" in out


def test_format_comparison_removed():
    diff = {"added": [], "removed": ["0 1 * * *"], "unchanged": []}
    out = format_comparison(diff, "old", "new")
    assert "-" in out
    assert "0 1 * * *" in out


def test_format_comparison_no_changes():
    diff = {"added": [], "removed": [], "unchanged": ["* * * * *"]}
    out = format_comparison(diff, "a", "b")
    assert "No changes" in out


def test_format_list_empty():
    assert "No snapshots" in format_list([])


def test_format_list_names():
    out = format_list(["alpha", "beta"])
    assert "alpha" in out
    assert "beta" in out

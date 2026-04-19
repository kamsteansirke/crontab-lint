import pytest
from crontab_lint.watchlist import Watchlist, WatchedExpression, add
from crontab_lint.watchlist_formatter import format_entry, format_watchlist, format_summary


@pytest.fixture
def entry():
    return WatchedExpression(expression="0 0 * * *", label="daily", notes="runs at midnight", tags=["prod"])


def test_format_entry_contains_label(entry):
    result = format_entry(entry)
    assert "daily" in result


def test_format_entry_contains_expression(entry):
    result = format_entry(entry)
    assert "0 0 * * *" in result


def test_format_entry_with_index(entry):
    result = format_entry(entry, index=3)
    assert result.startswith("3.")


def test_format_entry_no_index(entry):
    result = format_entry(entry, index=None)
    assert not result.startswith("1.")


def test_format_entry_shows_tags(entry):
    result = format_entry(entry)
    assert "prod" in result


def test_format_entry_shows_notes(entry):
    result = format_entry(entry)
    assert "midnight" in result


def test_format_entry_no_tags_or_notes():
    e = WatchedExpression(expression="* * * * *", label="every")
    result = format_entry(e)
    assert "tags" not in result
    assert "notes" not in result


def test_format_watchlist_empty():
    wl = Watchlist()
    result = format_watchlist(wl)
    assert "empty" in result.lower()


def test_format_watchlist_multiple():
    wl = Watchlist()
    add(wl, "0 * * * *", "hourly")
    add(wl, "0 0 * * *", "daily")
    result = format_watchlist(wl)
    assert "hourly" in result
    assert "daily" in result


def test_format_summary_count():
    wl = Watchlist()
    add(wl, "* * * * *", "a")
    add(wl, "0 * * * *", "b")
    result = format_summary(wl)
    assert "2" in result

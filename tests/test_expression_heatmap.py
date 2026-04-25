"""Tests for expression_heatmap and expression_heatmap_formatter."""
import pytest
from crontab_lint.expression_heatmap import build_heatmap, HeatmapCell
from crontab_lint.expression_heatmap_formatter import format_heatmap, format_summary


def test_invalid_expression_returns_invalid_heatmap():
    h = build_heatmap("not a cron")
    assert not h.is_valid
    assert h.error is not None
    assert h.cells == []


def test_every_minute_has_cells():
    h = build_heatmap("* * * * *")
    assert h.is_valid
    assert len(h.cells) > 0


def test_every_minute_total_weekly_runs():
    h = build_heatmap("* * * * *")
    # 60 minutes * 24 hours * 7 days
    assert h.total_weekly_runs() == 60 * 24 * 7


def test_once_daily_midnight_has_correct_cells():
    h = build_heatmap("0 0 * * *")
    assert h.is_valid
    # 7 days, each with 1 run at hour 0
    assert all(c.hour == 0 for c in h.cells)
    assert h.total_weekly_runs() == 7


def test_specific_dow_limits_cells():
    # every minute on Monday only (dow=1 in cron)
    h = build_heatmap("* * * * 1")
    assert h.is_valid
    assert all(c.dow == 0 for c in h.cells)  # Monday = dow index 0


def test_peak_hour_is_set_for_valid():
    h = build_heatmap("0 14 * * *")
    assert h.is_valid
    assert h.peak_hour == 14


def test_format_heatmap_contains_expression():
    h = build_heatmap("0 9 * * 1")
    out = format_heatmap(h)
    assert "0 9 * * 1" in out


def test_format_heatmap_invalid_shows_error():
    h = build_heatmap("bad expr")
    out = format_heatmap(h)
    assert "invalid" in out.lower()


def test_format_heatmap_contains_day_labels():
    h = build_heatmap("* * * * *")
    out = format_heatmap(h)
    assert "Mon" in out
    assert "Sun" in out


def test_format_summary_counts_valid():
    heatmaps = [build_heatmap("* * * * *"), build_heatmap("bad"), build_heatmap("0 0 * * *")]
    out = format_summary(heatmaps)
    assert "2/3" in out


def test_heatmap_cell_fields():
    cell = HeatmapCell(hour=10, dow=2, runs_per_week=60)
    assert cell.hour == 10
    assert cell.dow == 2
    assert cell.runs_per_week == 60

"""Tests for crontab_lint.expression_pauser."""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

from crontab_lint.expression_pauser import PausedExpression, PauseStore


@pytest.fixture
def tmp_store(tmp_path: Path) -> PauseStore:
    return PauseStore(tmp_path / "paused.json")


def _future() -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()


def _past() -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()


# --- PausedExpression unit tests ---

def test_is_expired_no_resume_at():
    e = PausedExpression(expression="* * * * *", label="job")
    assert e.is_expired() is False


def test_is_expired_future_resume_at():
    e = PausedExpression(expression="* * * * *", label="job", resume_at=_future())
    assert e.is_expired() is False


def test_is_expired_past_resume_at():
    e = PausedExpression(expression="* * * * *", label="job", resume_at=_past())
    assert e.is_expired() is True


def test_roundtrip_serialization():
    e = PausedExpression(expression="0 9 * * 1", label="weekly", reason="maintenance")
    restored = PausedExpression.from_dict(e.to_dict())
    assert restored.expression == e.expression
    assert restored.label == e.label
    assert restored.reason == e.reason


# --- PauseStore tests ---

def test_pause_and_find(tmp_store: PauseStore):
    entry = PausedExpression(expression="0 6 * * *", label="morning")
    tmp_store.pause(entry)
    found = tmp_store.find("morning")
    assert found is not None
    assert found.expression == "0 6 * * *"


def test_find_missing_returns_none(tmp_store: PauseStore):
    assert tmp_store.find("nonexistent") is None


def test_resume_existing(tmp_store: PauseStore):
    entry = PausedExpression(expression="0 6 * * *", label="morning")
    tmp_store.pause(entry)
    result = tmp_store.resume("morning")
    assert result is True
    assert tmp_store.find("morning") is None


def test_resume_missing_returns_false(tmp_store: PauseStore):
    assert tmp_store.resume("ghost") is False


def test_pause_replaces_existing_label(tmp_store: PauseStore):
    e1 = PausedExpression(expression="0 6 * * *", label="job", reason="first")
    e2 = PausedExpression(expression="0 9 * * *", label="job", reason="second")
    tmp_store.pause(e1)
    tmp_store.pause(e2)
    assert len(tmp_store.all()) == 1
    assert tmp_store.find("job").reason == "second"


def test_all_active_excludes_expired(tmp_store: PauseStore):
    active = PausedExpression(expression="0 6 * * *", label="active", resume_at=_future())
    expired = PausedExpression(expression="0 7 * * *", label="expired", resume_at=_past())
    tmp_store.pause(active)
    tmp_store.pause(expired)
    active_list = tmp_store.all_active()
    labels = [e.label for e in active_list]
    assert "active" in labels
    assert "expired" not in labels


def test_purge_expired_removes_expired_entries(tmp_store: PauseStore):
    tmp_store.pause(PausedExpression(expression="* * * * *", label="keep"))
    tmp_store.pause(PausedExpression(expression="0 1 * * *", label="drop", resume_at=_past()))
    removed = tmp_store.purge_expired()
    assert removed == 1
    assert tmp_store.find("keep") is not None
    assert tmp_store.find("drop") is None


def test_store_persists_to_disk(tmp_path: Path):
    p = tmp_path / "paused.json"
    s1 = PauseStore(p)
    s1.pause(PausedExpression(expression="0 0 * * *", label="midnight"))
    s2 = PauseStore(p)
    assert s2.find("midnight") is not None

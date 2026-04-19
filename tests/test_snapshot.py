import pytest
from crontab_lint.snapshot import Snapshot, SnapshotStore, add, find, remove, compare


@pytest.fixture
def tmp_store(tmp_path):
    return SnapshotStore.load(tmp_path / "snaps.json")


def _snap(name="s1", exprs=None):
    return Snapshot(name=name, expressions=exprs or ["* * * * *"])


def test_add_and_find(tmp_store):
    add(tmp_store, _snap("a"))
    assert find(tmp_store, "a") is not None


def test_find_missing_returns_none(tmp_store):
    assert find(tmp_store, "nope") is None


def test_add_replaces_existing(tmp_store):
    add(tmp_store, _snap("a", ["* * * * *"]))
    add(tmp_store, _snap("a", ["0 * * * *"]))
    s = find(tmp_store, "a")
    assert s.expressions == ["0 * * * *"]
    assert len(tmp_store.snapshots) == 1


def test_remove_existing(tmp_store):
    add(tmp_store, _snap("a"))
    assert remove(tmp_store, "a") is True
    assert find(tmp_store, "a") is None


def test_remove_missing(tmp_store):
    assert remove(tmp_store, "ghost") is False


def test_save_and_load_roundtrip(tmp_path):
    path = tmp_path / "snaps.json"
    store = SnapshotStore.load(path)
    add(store, Snapshot(name="x", expressions=["5 4 * * *"], created_at="2024-01-01"))
    store2 = SnapshotStore.load(path)
    s = find(store2, "x")
    assert s is not None
    assert s.expressions == ["5 4 * * *"]
    assert s.created_at == "2024-01-01"


def test_compare_added_removed():
    old = Snapshot("o", ["* * * * *", "0 1 * * *"])
    new = Snapshot("n", ["* * * * *", "0 2 * * *"])
    diff = compare(old, new)
    assert "0 2 * * *" in diff["added"]
    assert "0 1 * * *" in diff["removed"]
    assert "* * * * *" in diff["unchanged"]


def test_compare_no_changes():
    snap = Snapshot("s", ["* * * * *"])
    diff = compare(snap, snap)
    assert diff["added"] == []
    assert diff["removed"] == []

"""Tests for crontab_lint.profile."""
import pytest
from pathlib import Path
from crontab_lint.profile import Profile, ProfileStore


@pytest.fixture
def tmp_store(tmp_path: Path) -> ProfileStore:
    return ProfileStore(tmp_path / "profiles.json")


def test_profile_add_expression():
    p = Profile(name="daily")
    p.add_expression("0 0 * * *")
    assert "0 0 * * *" in p.expressions


def test_profile_add_expression_no_duplicates():
    p = Profile(name="daily")
    p.add_expression("0 0 * * *")
    p.add_expression("0 0 * * *")
    assert p.expressions.count("0 0 * * *") == 1


def test_profile_remove_expression_existing():
    p = Profile(name="daily", expressions=["0 0 * * *"])
    result = p.remove_expression("0 0 * * *")
    assert result is True
    assert p.expressions == []


def test_profile_remove_expression_missing():
    p = Profile(name="daily")
    result = p.remove_expression("0 0 * * *")
    assert result is False


def test_profile_has_tag():
    p = Profile(name="daily", tags=["prod", "nightly"])
    assert p.has_tag("prod")
    assert not p.has_tag("staging")


def test_store_add_and_find(tmp_store: ProfileStore):
    p = Profile(name="weekly", description="Weekly jobs")
    tmp_store.add(p)
    found = tmp_store.find("weekly")
    assert found is not None
    assert found.description == "Weekly jobs"


def test_store_find_missing_returns_none(tmp_store: ProfileStore):
    assert tmp_store.find("ghost") is None


def test_store_add_replaces_existing(tmp_store: ProfileStore):
    tmp_store.add(Profile(name="x", description="old"))
    tmp_store.add(Profile(name="x", description="new"))
    assert len(tmp_store.all()) == 1
    assert tmp_store.find("x").description == "new"


def test_store_remove_existing(tmp_store: ProfileStore):
    tmp_store.add(Profile(name="removeme"))
    result = tmp_store.remove("removeme")
    assert result is True
    assert tmp_store.find("removeme") is None


def test_store_remove_missing(tmp_store: ProfileStore):
    assert tmp_store.remove("nope") is False


def test_store_find_by_tag(tmp_store: ProfileStore):
    tmp_store.add(Profile(name="a", tags=["prod"]))
    tmp_store.add(Profile(name="b", tags=["staging"]))
    tmp_store.add(Profile(name="c", tags=["prod", "nightly"]))
    results = tmp_store.find_by_tag("prod")
    names = [p.name for p in results]
    assert "a" in names and "c" in names and "b" not in names


def test_store_persists_across_instances(tmp_path: Path):
    path = tmp_path / "profiles.json"
    s1 = ProfileStore(path)
    s1.add(Profile(name="persistent", description="saved"))
    s2 = ProfileStore(path)
    assert s2.find("persistent") is not None

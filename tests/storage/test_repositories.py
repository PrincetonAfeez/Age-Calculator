"""Test the repositories module."""

from datetime import UTC, date, datetime

import pytest

from agecalc.domain import Profile
from agecalc.exceptions import UnknownProfileError
from agecalc.storage import InMemoryProfileRepository, SQLiteProfileRepository


@pytest.fixture
def profile() -> Profile:
    return Profile(
        name="Ada",
        birthdate=date(1815, 12, 10),
        created_at=datetime(2025, 1, 1, tzinfo=UTC),
    )


def test_in_memory_repository_round_trip(profile: Profile) -> None:
    repository = InMemoryProfileRepository()

    repository.save(profile)

    assert repository.get("ada") == profile
    assert repository.list() == [profile]


def test_in_memory_repository_delete(profile: Profile) -> None:
    repository = InMemoryProfileRepository()
    repository.save(profile)

    repository.delete("Ada")

    with pytest.raises(UnknownProfileError):
        repository.get("Ada")


def test_sqlite_repository_round_trip(tmp_path, profile: Profile) -> None:
    repository = SQLiteProfileRepository(tmp_path / "profiles.sqlite3")

    repository.save(profile)

    assert repository.get("Ada") == profile
    assert repository.list() == [profile]

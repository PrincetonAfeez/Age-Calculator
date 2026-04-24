"""Test the calculations module."""

from datetime import date, timedelta

import pytest
from hypothesis import given
from hypothesis import strategies as st

from agecalc.calculations import age_at, milestones, reference_date


@pytest.mark.parametrize(
    ("birthdate", "reference", "expected"),
    [
        (date(2025, 4, 21), date(2025, 4, 21), (0, 0, 0)),
        (date(2025, 4, 20), date(2025, 4, 21), (0, 0, 1)),
        (date(2000, 2, 29), date(2025, 2, 28), (25, 0, 0)),
        (date(2025, 4, 20), date(2025, 4, 20), (0, 0, 0)),
    ],
)
def test_age_at_edge_cases(
    birthdate: date,
    reference: date,
    expected: tuple[int, int, int],
) -> None:
    age = age_at(birthdate, reference)

    assert (age.years, age.months, age.days) == expected


def test_age_one_second_before_midnight_as_dates() -> None:
    age = age_at(date(2025, 4, 20), date(2025, 4, 21))

    assert age.total_seconds == 24 * 60 * 60


def test_reference_date_context_manager_freezes_today() -> None:
    with reference_date(date(2025, 4, 21)):
        age = age_at(date(2020, 4, 21))

    assert age.years == 5


def test_milestones_are_sorted_and_limited() -> None:
    items = list(milestones(date(2020, 1, 1), date(2025, 1, 1), limit=5))

    assert len(items) == 5
    assert [item.target_date for item in items] == sorted(item.target_date for item in items)


@given(
    birthdate=st.dates(min_value=date(1900, 1, 1), max_value=date(2090, 12, 31)),
    days_after=st.integers(min_value=1, max_value=10_000),
)
def test_total_days_matches_elapsed_days(birthdate: date, days_after: int) -> None:
    reference = birthdate + timedelta(days=days_after)

    assert age_at(birthdate, reference).total_days == days_after

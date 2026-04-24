"""Test the age module."""

from datetime import date, datetime

import pytest

from agecalc.calculations import age_at
from agecalc.domain import Age
from agecalc.exceptions import FutureBirthDateError
from agecalc.factory import create_age


def test_age_formatting_and_repr() -> None:
    age = Age(years=2, months=3, days=4, total_seconds=800 * 24 * 60 * 60)

    assert f"{age:ymd}" == "2 years, 3 months, 4 days"
    assert f"{age:days}" == "800"
    assert repr(age) == "Age(years=2, months=3, days=4, total_seconds=69120000)"


def test_age_ordering_and_subtraction() -> None:
    younger = Age(years=1, months=0, days=0, total_seconds=100)
    older = Age(years=2, months=0, days=0, total_seconds=1_000)

    assert younger < older
    assert older - younger == Age.from_total_seconds(900)


@pytest.mark.parametrize(
    ("value", "expected_years"),
    [
        ("2000-01-01", 25),
        (date(2000, 1, 1), 25),
        (datetime(2000, 1, 1, 23, 59), 25),
        ((2000, 1, 1), 25),
    ],
)
def test_create_age_with_singledispatch(value: object, expected_years: int) -> None:
    assert create_age(value, date(2025, 1, 1)).years == expected_years


def test_future_birthdate_raises() -> None:
    with pytest.raises(FutureBirthDateError):
        age_at(date(2030, 1, 1), date(2025, 1, 1))

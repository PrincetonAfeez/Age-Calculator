"""Test the parsing module."""

from datetime import date

import pytest

from agecalc.exceptions import AmbiguousDateError, InvalidDateError
from agecalc.parsing import ParserRegistry, default_registry


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("2025-04-21", date(2025, 4, 21)),
        ("04/21/2025", date(2025, 4, 21)),
        ("21/04/2025", date(2025, 4, 21)),
    ],
)
def test_registry_parses_supported_formats(raw_value: str, expected: date) -> None:
    assert default_registry().parse(raw_value) == expected


def test_registry_detects_ambiguous_dates() -> None:
    with pytest.raises(AmbiguousDateError):
        default_registry().parse("03/04/2000")


def test_registry_rejects_unknown_format() -> None:
    with pytest.raises(InvalidDateError):
        default_registry().parse("April 21, 2025")


def test_registry_requires_parser() -> None:
    with pytest.raises(ValueError):
        ParserRegistry([])

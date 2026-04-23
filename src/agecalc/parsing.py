"""Date parsing strategies and registry."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Protocol

from agecalc.exceptions import AmbiguousDateError, InvalidDateError


class DateParser(Protocol):
    """Strategy interface for parsing one date format."""

    @property
    def name(self) -> str:
        raise NotImplementedError

    def parse(self, raw_value: str) -> date:
        raise NotImplementedError
        """Return a date or raise InvalidDateError."""


@dataclass(frozen=True)
class _StrptimeParser:
    """Base class for parsers that use strptime."""
    name: str
    pattern: str

    def parse(self, raw_value: str) -> date:
        try:
            return datetime.strptime(raw_value, self.pattern).date()
        except ValueError as exc:
            msg = f"{raw_value!r} is not a valid {self.name} date."
            raise InvalidDateError(msg) from exc


class ISOParser(_StrptimeParser):
    def __init__(self) -> None:
        super().__init__(name="iso", pattern="%Y-%m-%d")


class USParser(_StrptimeParser):
    def __init__(self) -> None:
        super().__init__(name="us", pattern="%m/%d/%Y")


class EUParser(_StrptimeParser):
    def __init__(self) -> None:
        super().__init__(name="eu", pattern="%d/%m/%Y")


class ParserRegistry:
    """Tries parser strategies in order and detects conflicting successes."""

    def __init__(self, parsers: list[DateParser]) -> None:
        if not parsers:
            msg = "ParserRegistry needs at least one parser."
            raise ValueError(msg)
        self._parsers = parsers

    @property
    def parsers(self) -> tuple[DateParser, ...]:
        return tuple(self._parsers)

    def parse(self, raw_value: str) -> date:
        cleaned = raw_value.strip()
        matches: dict[str, date] = {}
        for parser in self._parsers:
            try:
                matches[parser.name] = parser.parse(cleaned)
            except InvalidDateError:
                continue

        if not matches:
            msg = f"Could not parse {raw_value!r} as ISO, US, or EU date."
            raise InvalidDateError(msg)

        unique_dates = set(matches.values())
        if len(unique_dates) > 1:
            raise AmbiguousDateError(raw_value, matches)

        return next(iter(unique_dates))


def default_registry(preferred: str = "iso") -> ParserRegistry:
    """Return a registry with ISO, US, and EU parsers, prioritizing the preferred format."""
    parser_map: dict[str, DateParser] = {
        "iso": ISOParser(),
        "us": USParser(),
        "eu": EUParser(),
    }
    ordered_names = [preferred, *[name for name in ("iso", "us", "eu") if name != preferred]]
    return ParserRegistry([parser_map[name] for name in ordered_names if name in parser_map])

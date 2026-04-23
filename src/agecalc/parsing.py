from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Protocol

from agecalc.exceptions import AmbiguousDateError, InvalidDateError


class DateParser(Protocol):

    @property
    def name(self) -> str:
        raise NotImplementedError

    def parse(self, raw_value: str) -> date:
        raise NotImplementedError

@dataclass(frozen=True)
class _StrptimeParser:
    name: str
    pattern: str

    def parse(self, raw_value: str) -> date:
        try:
            return datetime.strptime(raw_value, self.pattern).date()
        except ValueError as exc:
            msg = f"{raw_value!r} is not a valid {self.name} date."
            raise InvalidDateError(msg) from exc

"""Core domain objects for the age calculator."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from functools import total_ordering
from typing import Any

SECONDS_PER_DAY = 24 * 60 * 60


@total_ordering
@dataclass(frozen=True, eq=False)
class Age:
    """Calendar age plus total elapsed seconds.

    ``years/months/days`` keep the human calendar representation, while
    ``total_seconds`` gives comparisons a single precise value.
    """

    years: int
    months: int
    days: int
    total_seconds: int

    def __post_init__(self) -> None:
        values = (self.years, self.months, self.days, self.total_seconds)
        if any(value < 0 for value in values):
            msg = "Age values cannot be negative."
            raise ValueError(msg)

    @property
    def total_days(self) -> int:
        """Whole elapsed days represented by this age."""

        return self.total_seconds // SECONDS_PER_DAY

    @classmethod
    def from_total_seconds(cls, total_seconds: int) -> Age:
        """Build a compact duration-like age from seconds.

        A pure second count has no start date, so months and years are only a
        conventional breakdown here. Calendar-accurate ages are produced by
        ``age_at``.
        """

        total_days = abs(total_seconds) // SECONDS_PER_DAY
        years, remaining_days = divmod(total_days, 365)
        months, days = divmod(remaining_days, 30)
        return cls(years=years, months=months, days=days, total_seconds=abs(total_seconds))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Age):
            return NotImplemented
        return self.total_seconds == other.total_seconds

    def __lt__(self, other: Age) -> bool:
        if not isinstance(other, Age):
            return NotImplemented
        return self.total_seconds < other.total_seconds

    def __sub__(self, other: Age) -> Age:
        if not isinstance(other, Age):
            return NotImplemented
        return Age.from_total_seconds(self.total_seconds - other.total_seconds)

    def __repr__(self) -> str:
        return (
            "Age("
            f"years={self.years}, "
            f"months={self.months}, "
            f"days={self.days}, "
            f"total_seconds={self.total_seconds}"
            ")"
        )

    def __format__(self, spec: str) -> str:
        if spec in {"", "ymd"}:
            return f"{self.years} years, {self.months} months, {self.days} days"
        if spec == "days":
            return str(self.total_days)
        if spec == "seconds":
            return str(self.total_seconds)
        msg = f"Unsupported Age format specifier: {spec!r}"
        raise ValueError(msg)


@dataclass(frozen=True)
class Profile:
    """Saved person/profile in the application domain."""

    name: str
    birthdate: date
    created_at: datetime

    @classmethod
    def create(cls, name: str, birthdate: date) -> Profile:
        clean_name = name.strip()
        if not clean_name:
            msg = "Profile name cannot be empty."
            raise ValueError(msg)
        return cls(
            name=clean_name,
            birthdate=birthdate,
            created_at=datetime.now(UTC),
        )

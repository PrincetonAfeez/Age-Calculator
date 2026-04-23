from __future__ import annotations

import heapq
from calendar import monthrange
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import date, timedelta
from functools import lru_cache, wraps
from itertools import count
from typing import Any, TypeVar, cast

from agecalc.domain import SECONDS_PER_DAY, Age
from agecalc.exceptions import FutureBirthDateError

F = TypeVar("F", bound=Callable[..., object])

_REFERENCE_DATE: ContextVar[date | None] = ContextVar("agecalc_reference_date", default=None)


def current_reference_date() -> date:
    override = _REFERENCE_DATE.get()
    return override if override is not None else date.today()


@contextmanager
def reference_date(value: date) -> Iterator[None]:
    token = _REFERENCE_DATE.set(value)
    try:
        yield
    finally:
        _REFERENCE_DATE.reset(token)


def validate_not_future(func: F) -> F:
    @wraps(func)
    def wrapper(
        birthdate: date,
        reference: date | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> object:
        resolved_reference = reference if reference is not None else current_reference_date()
        if birthdate > resolved_reference:
            msg = (
                f"Birthdate {birthdate.isoformat()} is after reference date "
                f"{resolved_reference.isoformat()}."
            )
            raise FutureBirthDateError(msg)
        return func(birthdate, resolved_reference, *args, **kwargs)

    return cast(F, wrapper)

def _birthday_in_year(birthdate: date, year: int) -> date:
    try:
        return birthdate.replace(year=year)
    except ValueError:
        return date(year, 2, 28)

def _add_months(start: date, months: int) -> date:
    month_index = start.month - 1 + months
    year = start.year + month_index // 12
    month = month_index % 12 + 1
    day = min(start.day, monthrange(year, month)[1])
    return date(year, month, day)

@validate_not_future
def age_at(birthdate: date, reference: date | None = None) -> Age:
    resolved_reference = reference if reference is not None else current_reference_date()
    years = resolved_reference.year - birthdate.year
    anniversary = _birthday_in_year(birthdate, birthdate.year + years)

    if anniversary > resolved_reference:
        years -= 1
        anniversary = _birthday_in_year(birthdate, birthdate.year + years)

    months = 0
    cursor = anniversary
    while True:
        candidate = _add_months(cursor, 1)
        if candidate > resolved_reference:
            break
        months += 1
        cursor = candidate

    days = (resolved_reference - cursor).days
    total_seconds = (resolved_reference - birthdate).days * SECONDS_PER_DAY
    return Age(years=years, months=months, days=days, total_seconds=total_seconds)


@lru_cache(maxsize=2048)
def day_of_week(value: date) -> str:
    return value.strftime("%A")


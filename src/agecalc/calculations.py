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


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

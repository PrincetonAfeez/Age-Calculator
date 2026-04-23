from __future__ import annotations

from datetime import date, datetime
from functools import singledispatch
from typing import Any

from agecalc.calculations import age_at
from agecalc.domain import Age
from agecalc.exceptions import InvalidDateError
from agecalc.parsing import ParserRegistry, default_registry

@singledispatch
def create_age(
    value: object,
    reference: date | None = None,
    registry: ParserRegistry | None = None,
) -> Age:
    msg = f"Cannot create an age from {type(value).__name__}."
    raise InvalidDateError(msg)

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

@create_age.register
def _from_string(
    value: str,
    reference: date | None = None,
    registry: ParserRegistry | None = None,
) -> Age:
    active_registry = registry if registry is not None else default_registry()
    return age_at(active_registry.parse(value), reference)

@create_age.register
def _from_date(
    value: date,
    reference: date | None = None,
    registry: ParserRegistry | None = None,
) -> Age:
    return age_at(value, reference)

@create_age.register
def _from_datetime(
    value: datetime,
    reference: date | None = None,
    registry: ParserRegistry | None = None,
) -> Age:
    return age_at(value.date(), reference)

@create_age.register(tuple)
def _from_tuple(
    value: tuple[Any, ...],
    reference: date | None = None,
    registry: ParserRegistry | None = None,
) -> Age:
    if len(value) != 3:
        msg = "Tuple birthdates must be in (year, month, day) form."
        raise InvalidDateError(msg)
    try:
        year, month, day = (int(part) for part in value)
        birthdate = date(year, month, day)
    except (TypeError, ValueError) as exc:
        msg = f"Tuple {value!r} is not a valid date."
        raise InvalidDateError(msg) from exc
    return age_at(birthdate, reference)


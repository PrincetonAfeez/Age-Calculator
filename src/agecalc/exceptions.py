"""Project-specific exception hierarchy."""

from __future__ import annotations

from datetime import date


class AgeCalcError(Exception):
    """Base exception for all application-level errors."""


class InvalidDateError(AgeCalcError):
    """Raised when input cannot be interpreted as a valid date."""


class AmbiguousDateError(InvalidDateError):
    """Raised when the same text can mean multiple different dates."""

    def __init__(self, raw_value: str, candidates: dict[str, date]) -> None:
        choices = ", ".join(f"{name}={value.isoformat()}" for name, value in candidates.items())
        super().__init__(f"Ambiguous date {raw_value!r}; possible interpretations: {choices}")
        self.raw_value = raw_value
        self.candidates = candidates


class FutureBirthDateError(InvalidDateError):
    """Raised when a birthdate is later than the reference date."""


class UnknownProfileError(AgeCalcError):
    """Raised when a requested saved profile does not exist."""

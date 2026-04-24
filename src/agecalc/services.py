"""Application services that coordinate domain logic."""

from __future__ import annotations

from datetime import date

from agecalc.calculations import Milestone, age_at, milestones
from agecalc.domain import Age, Profile
from agecalc.factory import create_age, normalize_birthdate
from agecalc.parsing import ParserRegistry, default_registry
from agecalc.storage import ProfileRepository


class AgeService:
    """Application service for one-off age calculations."""

    def __init__(self, parser_registry: ParserRegistry | None = None) -> None:
        """Initialize the age service."""
        self._parser_registry = (
            parser_registry if parser_registry is not None else default_registry()
        )

    def calculate(self, value: object, reference: date | None = None) -> Age:
        """Calculate the age for a given value and reference date."""
        return create_age(value, reference, self._parser_registry)

    def difference(self, left: object, right: object, reference: date | None = None) -> Age:
        """Calculate the difference between two values and a reference date."""
        return self.calculate(left, reference) - self.calculate(right, reference)

    def upcoming_milestones(
        self,
        value: object,
        reference: date | None = None,
        *,
        limit: int = 10,
    ) -> list[Milestone]:
        """Calculate the upcoming milestones for a given value and reference date."""
        birthdate = normalize_birthdate(value, self._parser_registry)
        return list(milestones(birthdate, reference, limit=limit))


class ProfileService:
    """Application service for saved profile workflows."""

    def __init__(
        self,
        repository: ProfileRepository,
        parser_registry: ParserRegistry | None = None,
    ) -> None:
        """Initialize the profile service."""
        self._repository = repository
        self._parser_registry = (
            parser_registry if parser_registry is not None else default_registry()
        )

    def add(self, name: str, birthdate_value: object) -> Profile:
        """Add a new profile or update an existing one."""
        birthdate = normalize_birthdate(birthdate_value, self._parser_registry)
        profile = Profile.create(name=name, birthdate=birthdate)
        self._repository.save(profile)
        return profile

    def get(self, name: str) -> Profile:
        """Get a profile by name."""
        return self._repository.get(name)

    def list_profiles(self) -> list[Profile]:
        """List all profiles."""
        return self._repository.list()

    def delete(self, name: str) -> None:
        """Delete a profile by name."""
        self._repository.delete(name)

    def age_for(self, name: str, reference: date | None = None) -> Age:
        """Calculate the age for a given profile and reference date."""
        profile = self.get(name)
        return age_at(profile.birthdate, reference)

    def milestones_for(
        self,
        name: str,
        reference: date | None = None,
        *,
        limit: int = 10,
    ) -> list[Milestone]:
        """Calculate the upcoming milestones for a given profile and reference date."""
        profile = self.get(name)
        return list(milestones(profile.birthdate, reference, limit=limit))

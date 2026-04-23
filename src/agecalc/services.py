from __future__ import annotations

from datetime import date

from agecalc.calculations import Milestone, age_at, milestones
from agecalc.domain import Age, Profile
from agecalc.factory import create_age, normalize_birthdate
from agecalc.parsing import ParserRegistry, default_registry
from agecalc.storage import ProfileRepository


class AgeService:
    def __init__(self, parser_registry: ParserRegistry | None = None) -> None:
        self._parser_registry = (
            parser_registry if parser_registry is not None else default_registry()
        )

    def calculate(self, value: object, reference: date | None = None) -> Age:
        return create_age(value, reference, self._parser_registry)

    def difference(self, left: object, right: object, reference: date | None = None) -> Age:
        return self.calculate(left, reference) - self.calculate(right, reference)

    def upcoming_milestones(
        self,
        value: object,
        reference: date | None = None,
        *,
        limit: int = 10,
    ) -> list[Milestone]:
        birthdate = normalize_birthdate(value, self._parser_registry)
        return list(milestones(birthdate, reference, limit=limit))

class ProfileService:
    def __init__(
        self,
        repository: ProfileRepository,
        parser_registry: ParserRegistry | None = None,
    ) -> None:
        self._repository = repository
        self._parser_registry = (
            parser_registry if parser_registry is not None else default_registry()
        )

    def add(self, name: str, birthdate_value: object) -> Profile:
        birthdate = normalize_birthdate(birthdate_value, self._parser_registry)
        profile = Profile.create(name=name, birthdate=birthdate)
        self._repository.save(profile)
        return profile

    def get(self, name: str) -> Profile:
        return self._repository.get(name)

    def list_profiles(self) -> list[Profile]:
        return self._repository.list()

    def delete(self, name: str) -> None:
        self._repository.delete(name)

    def age_for(self, name: str, reference: date | None = None) -> Age:
        profile = self.get(name)
        return age_at(profile.birthdate, reference)

    def milestones_for(
        self,
        name: str,
        reference: date | None = None,
        *,
        limit: int = 10,
    ) -> list[Milestone]:
        profile = self.get(name)
        return list(milestones(profile.birthdate, reference, limit=limit))

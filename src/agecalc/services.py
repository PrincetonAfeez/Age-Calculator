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

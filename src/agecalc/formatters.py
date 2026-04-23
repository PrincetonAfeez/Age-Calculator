from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Protocol

from agecalc.calculations import Milestone
from agecalc.domain import Age, Profile


class OutputFormatter(Protocol):
    def format_age(self, age: Age) -> str:
        raise NotImplementedError

    def format_diff(self, age: Age) -> str:
        raise NotImplementedError

    def format_milestones(self, milestones: Sequence[Milestone]) -> str:
        raise NotImplementedError

    def format_profile(self, profile: Profile) -> str:
        raise NotImplementedError

    def format_profiles(self, profiles: Sequence[Profile]) -> str:
        raise NotImplementedError

    def format_message(self, message: str) -> str:
        raise NotImplementedError

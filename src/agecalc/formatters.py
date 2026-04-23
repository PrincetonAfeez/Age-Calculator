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

def _age_dict(age: Age) -> dict[str, int]:
    return {
        "years": age.years,
        "months": age.months,
        "days": age.days,
        "total_days": age.total_days,
        "total_seconds": age.total_seconds,
    }

def _milestone_dict(milestone: Milestone) -> dict[str, str | int]:
    return {
        "label": milestone.label,
        "target_date": milestone.target_date.isoformat(),
        "days_until": milestone.days_until,
        "weekday": milestone.weekday,
    }


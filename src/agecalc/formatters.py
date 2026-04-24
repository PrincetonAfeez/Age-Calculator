"""Output formatter strategies for the CLI."""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Protocol

from agecalc.calculations import Milestone
from agecalc.domain import Age, Profile


class OutputFormatter(Protocol):
    """Strategy interface for formatting output."""
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
    """Convert an Age to a dictionary."""
    return {
        "years": age.years,
        "months": age.months,
        "days": age.days,
        "total_days": age.total_days,
        "total_seconds": age.total_seconds,
    }


def _milestone_dict(milestone: Milestone) -> dict[str, str | int]:
    """Convert a Milestone to a dictionary."""
    return {
        "label": milestone.label,
        "target_date": milestone.target_date.isoformat(),
        "days_until": milestone.days_until,
        "weekday": milestone.weekday,
    }


def _profile_dict(profile: Profile) -> dict[str, str]:
    """Convert a Profile to a dictionary."""
    return {
        "name": profile.name,
        "birthdate": profile.birthdate.isoformat(),
        "created_at": profile.created_at.isoformat(),
    }


class PlainFormatter:
    """Plain text formatter for CLI output."""
    def format_age(self, age: Age) -> str:
        return f"Age: {age:ymd} ({age:days} days, {age:seconds} seconds)"

    def format_diff(self, age: Age) -> str:
        return f"Difference: {age:ymd} ({age:days} days)"

    def format_milestones(self, milestones: Sequence[Milestone]) -> str:
        if not milestones:
            return "No milestones found."
        lines = ["Upcoming milestones:"]
        for milestone in milestones:
            lines.append(
                "- "
                f"{milestone.label}: {milestone.target_date.isoformat()} "
                f"({milestone.weekday}, in {milestone.days_until} days)"
            )
        return "\n".join(lines)

    def format_profile(self, profile: Profile) -> str:
        return f"{profile.name}: born {profile.birthdate.isoformat()}"

    def format_profiles(self, profiles: Sequence[Profile]) -> str:
        if not profiles:
            return "No profiles saved."
        return "\n".join(self.format_profile(profile) for profile in profiles)

    def format_message(self, message: str) -> str:
        return message


class JSONFormatter:
    """JSON formatter for CLI output."""
    def format_age(self, age: Age) -> str:
        return json.dumps({"age": _age_dict(age)}, indent=2)

    def format_diff(self, age: Age) -> str:
        return json.dumps({"difference": _age_dict(age)}, indent=2)

    def format_milestones(self, milestones: Sequence[Milestone]) -> str:
        return json.dumps(
            {"milestones": [_milestone_dict(milestone) for milestone in milestones]},
            indent=2,
        )

    def format_profile(self, profile: Profile) -> str:
        return json.dumps({"profile": _profile_dict(profile)}, indent=2)

    def format_profiles(self, profiles: Sequence[Profile]) -> str:
        return json.dumps({"profiles": [_profile_dict(profile) for profile in profiles]}, indent=2)

    def format_message(self, message: str) -> str:
        return json.dumps({"message": message}, indent=2)


def formatter_for(name: str) -> OutputFormatter:
    """Return the appropriate formatter for the given name.""" 
    if name == "json":
        return JSONFormatter()
    return PlainFormatter()

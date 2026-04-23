from __future__ import annotations

import sqlite3
from abc import ABC, abstractmethod
from datetime import date, datetime
from pathlib import Path

from agecalc.domain import Profile
from agecalc.exceptions import UnknownProfileError


class ProfileRepository(ABC):
    @abstractmethod
    def save(self, profile: Profile) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, name: str) -> Profile:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> list[Profile]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, name: str) -> None:
        raise NotImplementedError

class InMemoryProfileRepository(ProfileRepository):
    def __init__(self) -> None:
        self._profiles: dict[str, Profile] = {}

    def save(self, profile: Profile) -> None:
        self._profiles[profile.name.casefold()] = profile

    def get(self, name: str) -> Profile:
        try:
            return self._profiles[name.casefold()]
        except KeyError as exc:
            msg = f"No profile named {name!r}."
            raise UnknownProfileError(msg) from exc

    def list(self) -> list[Profile]:
        return sorted(self._profiles.values(), key=lambda profile: profile.name.casefold())

    def delete(self, name: str) -> None:
        key = name.casefold()
        if key not in self._profiles:
            msg = f"No profile named {name!r}."
            raise UnknownProfileError(msg)
        del self._profiles[key]


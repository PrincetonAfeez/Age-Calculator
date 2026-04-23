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


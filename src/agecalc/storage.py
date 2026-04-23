"""Repository abstractions and implementations."""

from __future__ import annotations

import sqlite3
from abc import ABC, abstractmethod
from datetime import date, datetime
from pathlib import Path

from agecalc.domain import Profile
from agecalc.exceptions import UnknownProfileError


class ProfileRepository(ABC):
    """Repository interface for saved profiles."""

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
    """Fast repository for tests and dependency injection examples."""

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


class SQLiteProfileRepository(ProfileRepository):
    """SQLite-backed profile repository."""

    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path.expanduser()
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _ensure_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS profiles (
                    name TEXT PRIMARY KEY,
                    birthdate TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def save(self, profile: Profile) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO profiles (name, birthdate, created_at)
                VALUES (?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    birthdate = excluded.birthdate,
                    created_at = excluded.created_at
                """,
                (
                    profile.name,
                    profile.birthdate.isoformat(),
                    profile.created_at.isoformat(),
                ),
            )

    def get(self, name: str) -> Profile:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT name, birthdate, created_at FROM profiles WHERE lower(name) = lower(?)",
                (name,),
            ).fetchone()

        if row is None:
            msg = f"No profile named {name!r}."
            raise UnknownProfileError(msg)
        return self._row_to_profile(row)

    def list(self) -> list[Profile]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT name, birthdate, created_at FROM profiles ORDER BY lower(name)"
            ).fetchall()
        return [self._row_to_profile(row) for row in rows]

    def delete(self, name: str) -> None:
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM profiles WHERE lower(name) = lower(?)",
                (name,),
            )
        if cursor.rowcount == 0:
            msg = f"No profile named {name!r}."
            raise UnknownProfileError(msg)

    @staticmethod
    def _row_to_profile(row: sqlite3.Row) -> Profile:
        """Convert a SQLite row to a Profile."""
        return Profile(
            name=str(row["name"]),
            birthdate=date.fromisoformat(str(row["birthdate"])),
            created_at=datetime.fromisoformat(str(row["created_at"])),
        )

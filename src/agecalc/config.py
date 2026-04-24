"""Configuration loading using pathlib and tomllib."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from datetime import UTC, date, datetime, tzinfo
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_CONFIG_DIR = Path.home() / ".agecalc"
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / "config.toml"
DEFAULT_DATABASE_PATH = DEFAULT_CONFIG_DIR / "profiles.sqlite3"


@dataclass(frozen=True)
class Config:
    preferred_date_format: str = "iso"
    output_format: str = "plain"
    reference_timezone: str = "UTC"
    database_path: Path = DEFAULT_DATABASE_PATH


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> Config:
    config_path = path.expanduser()
    if not config_path.exists():
        return Config()

    with config_path.open("rb") as config_file:
        data = tomllib.load(config_file)

    database_value = data.get("database_path", DEFAULT_DATABASE_PATH)
    database_path = Path(str(database_value)).expanduser()

    return Config(
        preferred_date_format=str(data.get("preferred_date_format", "iso")),
        output_format=str(data.get("output_format", "plain")),
        reference_timezone=str(data.get("reference_timezone", "UTC")),
        database_path=database_path,
    )


def today_in_timezone(timezone_name: str) -> date:
    active_timezone: tzinfo
    try:
        active_timezone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        active_timezone = UTC
    return datetime.now(active_timezone).date()

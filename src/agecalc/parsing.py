from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Protocol

from agecalc.exceptions import AmbiguousDateError, InvalidDateError



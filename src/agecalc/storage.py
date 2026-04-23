from __future__ import annotations

import sqlite3
from abc import ABC, abstractmethod
from datetime import date, datetime
from pathlib import Path

from agecalc.domain import Profile
from agecalc.exceptions import UnknownProfileError



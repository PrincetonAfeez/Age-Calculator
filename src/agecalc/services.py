from __future__ import annotations

from datetime import date

from agecalc.calculations import Milestone, age_at, milestones
from agecalc.domain import Age, Profile
from agecalc.factory import create_age, normalize_birthdate
from agecalc.parsing import ParserRegistry, default_registry
from agecalc.storage import ProfileRepository


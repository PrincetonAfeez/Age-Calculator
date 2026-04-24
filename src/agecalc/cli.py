"""Argparse command line interface using command objects."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from typing import Protocol

from agecalc.config import Config, load_config, today_in_timezone
from agecalc.exceptions import AgeCalcError
from agecalc.formatters import OutputFormatter, formatter_for
from agecalc.parsing import ParserRegistry, default_registry
from agecalc.services import AgeService, ProfileService
from agecalc.storage import ProfileRepository, SQLiteProfileRepository


class Command(Protocol):
    def execute(self, args: argparse.Namespace) -> str:
        raise NotImplementedError


@dataclass(frozen=True)
class CommandContext:
    config: Config
    formatter: OutputFormatter
    age_service: AgeService
    profile_service: ProfileService
    parser_registry: ParserRegistry

    def today(self) -> date:
        return today_in_timezone(self.config.reference_timezone)


def _reference_from_args(args: argparse.Namespace, context: CommandContext) -> date:
    raw_reference = getattr(args, "reference", None)
    if raw_reference:
        return context.parser_registry.parse(str(raw_reference))
    return context.today()


class AgeCommand:
    def __init__(self, context: CommandContext) -> None:
        self._context = context

    def execute(self, args: argparse.Namespace) -> str:
        reference = _reference_from_args(args, self._context)
        age = self._context.age_service.calculate(args.birthdate, reference)
        return self._context.formatter.format_age(age)


class DiffCommand:
    def __init__(self, context: CommandContext) -> None:
        self._context = context

    def execute(self, args: argparse.Namespace) -> str:
        reference = _reference_from_args(args, self._context)
        difference = self._context.age_service.difference(args.left, args.right, reference)
        return self._context.formatter.format_diff(difference)


class MilestonesCommand:
    def __init__(self, context: CommandContext) -> None:
        self._context = context

    def execute(self, args: argparse.Namespace) -> str:
        reference = _reference_from_args(args, self._context)
        items = self._context.age_service.upcoming_milestones(
            args.birthdate,
            reference,
            limit=args.limit,
        )
        return self._context.formatter.format_milestones(items)


class ProfileAddCommand:
    def __init__(self, context: CommandContext) -> None:
        self._context = context

    def execute(self, args: argparse.Namespace) -> str:
        profile = self._context.profile_service.add(args.name, args.birthdate)
        return self._context.formatter.format_profile(profile)


class ProfileListCommand:
    def __init__(self, context: CommandContext) -> None:
        self._context = context

    def execute(self, args: argparse.Namespace) -> str:
        profiles = self._context.profile_service.list_profiles()
        return self._context.formatter.format_profiles(profiles)


class ProfileGetCommand:
    def __init__(self, context: CommandContext) -> None:
        self._context = context

    def execute(self, args: argparse.Namespace) -> str:
        return self._context.formatter.format_profile(self._context.profile_service.get(args.name))


class ProfileDeleteCommand:
    def __init__(self, context: CommandContext) -> None:
        self._context = context

    def execute(self, args: argparse.Namespace) -> str:
        self._context.profile_service.delete(args.name)
        return self._context.formatter.format_message(f"Deleted profile {args.name!r}.")


class ProfileAgeCommand:
    def __init__(self, context: CommandContext) -> None:
        self._context = context

    def execute(self, args: argparse.Namespace) -> str:
        reference = _reference_from_args(args, self._context)
        age = self._context.profile_service.age_for(args.name, reference)
        return self._context.formatter.format_age(age)


class ProfileMilestonesCommand:
    def __init__(self, context: CommandContext) -> None:
        self._context = context

    def execute(self, args: argparse.Namespace) -> str:
        reference = _reference_from_args(args, self._context)
        items = self._context.profile_service.milestones_for(
            args.name,
            reference,
            limit=args.limit,
        )
        return self._context.formatter.format_milestones(items)


CommandFactory = Callable[[CommandContext], Command]

COMMANDS: dict[str, CommandFactory] = {
    "age": AgeCommand,
    "diff": DiffCommand,
    "milestones": MilestonesCommand,
    "profile_add": ProfileAddCommand,
    "profile_list": ProfileListCommand,
    "profile_get": ProfileGetCommand,
    "profile_delete": ProfileDeleteCommand,
    "profile_age": ProfileAgeCommand,
    "profile_milestones": ProfileMilestonesCommand,
}


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        msg = f"{value!r} must be at least 1."
        raise argparse.ArgumentTypeError(msg)
    return parsed


def _add_format_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--format",
        choices=["plain", "json"],
        default=argparse.SUPPRESS,
        help="Output format.",
    )


def build_parser(config: Config) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agecalc", description="Calculate ages and milestones.")
    parser.add_argument(
        "--format",
        choices=["plain", "json"],
        default=config.output_format,
        help="Output format.",
    )

    subcommands = parser.add_subparsers(dest="command_name", required=True)

    age_parser = subcommands.add_parser("age", help="Calculate an age.")
    _add_format_option(age_parser)
    age_parser.add_argument("birthdate", help="Birthdate as YYYY-MM-DD, MM/DD/YYYY, or DD/MM/YYYY.")
    age_parser.add_argument("--reference", "-r", help="Reference date.")
    age_parser.set_defaults(command_name="age")

    diff_parser = subcommands.add_parser("diff", help="Calculate the difference between two ages.")
    _add_format_option(diff_parser)
    diff_parser.add_argument("left", help="First birthdate.")
    diff_parser.add_argument("right", help="Second birthdate.")
    diff_parser.add_argument("--reference", "-r", help="Reference date.")
    diff_parser.set_defaults(command_name="diff")

    milestones_parser = subcommands.add_parser("milestones", help="Show upcoming milestones.")
    _add_format_option(milestones_parser)
    milestones_parser.add_argument("birthdate", help="Birthdate.")
    milestones_parser.add_argument("--reference", "-r", help="Reference date.")
    milestones_parser.add_argument(
        "--limit",
        type=_positive_int,
        default=10,
        help="Number of milestones.",
    )
    milestones_parser.set_defaults(command_name="milestones")

    profile_parser = subcommands.add_parser("profile", help="Manage saved profiles.")
    _add_format_option(profile_parser)
    profile_subcommands = profile_parser.add_subparsers(dest="profile_command", required=True)

    profile_add = profile_subcommands.add_parser("add", help="Add or update a profile.")
    _add_format_option(profile_add)
    profile_add.add_argument("name")
    profile_add.add_argument("birthdate")
    profile_add.set_defaults(command_name="profile_add")

    profile_list = profile_subcommands.add_parser("list", help="List saved profiles.")
    _add_format_option(profile_list)
    profile_list.set_defaults(command_name="profile_list")

    profile_get = profile_subcommands.add_parser("get", help="Show one profile.")
    _add_format_option(profile_get)
    profile_get.add_argument("name")
    profile_get.set_defaults(command_name="profile_get")

    profile_delete = profile_subcommands.add_parser("delete", help="Delete one profile.")
    _add_format_option(profile_delete)
    profile_delete.add_argument("name")
    profile_delete.set_defaults(command_name="profile_delete")

    profile_age = profile_subcommands.add_parser("age", help="Calculate age for one profile.")
    _add_format_option(profile_age)
    profile_age.add_argument("name")
    profile_age.add_argument("--reference", "-r", help="Reference date.")
    profile_age.set_defaults(command_name="profile_age")

    profile_milestones = profile_subcommands.add_parser(
        "milestones",
        help="Show milestones for one profile.",
    )
    _add_format_option(profile_milestones)
    profile_milestones.add_argument("name")
    profile_milestones.add_argument("--reference", "-r", help="Reference date.")
    profile_milestones.add_argument(
        "--limit",
        type=_positive_int,
        default=10,
        help="Number of milestones.",
    )
    profile_milestones.set_defaults(command_name="profile_milestones")

    return parser


def _build_context(
    args: argparse.Namespace,
    config: Config,
    repository: ProfileRepository | None,
) -> CommandContext:
    parser_registry = default_registry(config.preferred_date_format)
    active_repository = (
        repository if repository is not None else SQLiteProfileRepository(config.database_path)
    )
    return CommandContext(
        config=config,
        formatter=formatter_for(args.format),
        age_service=AgeService(parser_registry),
        profile_service=ProfileService(active_repository, parser_registry),
        parser_registry=parser_registry,
    )


def main(argv: list[str] | None = None, repository: ProfileRepository | None = None) -> int:
    config = load_config()
    parser = build_parser(config)
    args = parser.parse_args(argv)
    context = _build_context(args, config, repository)

    try:
        command = COMMANDS[str(args.command_name)](context)
        print(command.execute(args))
    except AgeCalcError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0

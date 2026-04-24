"""Test the CLI."""

import json

import pytest

from agecalc.cli import main
from agecalc.storage import InMemoryProfileRepository


def test_cli_age_plain_output(capsys) -> None:
    exit_code = main(
        ["age", "2000-01-01", "--reference", "2025-01-01"],
        InMemoryProfileRepository(),
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Age: 25 years, 0 months, 0 days" in captured.out


def test_cli_json_output(capsys) -> None:
    exit_code = main(
        ["--format", "json", "age", "2000-01-01", "--reference", "2025-01-01"],
        InMemoryProfileRepository(),
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["age"]["years"] == 25


def test_cli_profile_workflow(capsys) -> None:
    repository = InMemoryProfileRepository()

    assert main(["profile", "add", "Ada", "1815-12-10"], repository) == 0
    assert main(["profile", "list"], repository) == 0

    captured = capsys.readouterr()
    assert "Ada: born 1815-12-10" in captured.out


def test_cli_errors_are_user_friendly(capsys) -> None:
    exit_code = main(["age", "not-a-date"], InMemoryProfileRepository())

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "error:" in captured.err


def test_cli_json_output_when_format_after_subcommand(capsys) -> None:
    exit_code = main(
        ["milestones", "2000-01-01", "--format", "json", "--limit", "1"],
        InMemoryProfileRepository(),
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert len(payload["milestones"]) == 1


def test_cli_rejects_non_positive_limit(capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["milestones", "2000-01-01", "--limit", "0"], InMemoryProfileRepository())

    captured = capsys.readouterr()
    assert exc.value.code == 2
    assert "must be at least 1" in captured.err

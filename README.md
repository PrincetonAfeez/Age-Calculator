# Age Calculator

A feature-rich Python CLI age calculator built as a small layered application. It is intentionally written to show solid Python fundamentals, OOP, testing habits, and beginner-friendly system architecture.

## Install

```powershell
python -m pip install -e .[dev]
```

Then run:

```powershell
agecalc --help
```

## Usage Examples

```powershell
agecalc age 2000-02-29 --reference 2025-02-28
```

```powershell
agecalc --format json milestones 1998-07-12 --limit 3
```

`--format` can be passed either globally or after a subcommand:

```powershell
agecalc --format json milestones 1998-07-12 --limit 3
agecalc milestones 1998-07-12 --limit 3 --format json
```

```powershell
agecalc profile add Ada 1815-12-10
agecalc profile age Ada --reference 1852-11-27
agecalc profile list
```

## Configuration

The CLI reads optional settings from `~/.agecalc/config.toml`.

```toml
preferred_date_format = "iso"
output_format = "plain"
reference_timezone = "America/Los_Angeles"
database_path = "~/.agecalc/profiles.sqlite3"
```

Supported date inputs:

- ISO: `YYYY-MM-DD`
- US: `MM/DD/YYYY`
- EU: `DD/MM/YYYY`

If a date like `03/04/2000` can mean two different dates, the parser raises an ambiguity error instead of guessing.

## Architecture

```text
+-------------------+       +-------------------+
| argparse CLI      | ----> | Command objects   |
+-------------------+       +-------------------+
                                |
                                v
+-------------------+       +-------------------+
| OutputFormatter   | <---- | Application       |
| Plain / JSON      |       | Services          |
+-------------------+       +-------------------+
                                |
                 +--------------+--------------+
                 v                             v
       +-------------------+       +-----------------------+
       | Domain / Pure     |       | ProfileRepository ABC |
       | Calculations      |       | SQLite / InMemory     |
       +-------------------+       +-----------------------+
```

The CLI only parses arguments and formats output. Services coordinate use cases. Domain modules handle age math, parsing, and exceptions. Repositories hide storage details behind an interface, which keeps tests fast with `InMemoryProfileRepository`.

## What This Demonstrates

- Immutable dataclasses with `Age` and `Profile`
- Operator overloading with equality, ordering, subtraction, `repr`, and custom `format`
- Custom exception hierarchy rooted at `AgeCalcError`
- `functools.singledispatch` for age creation from strings, dates, datetimes, and tuples
- Strategy pattern through `DateParser`, `ISOParser`, `USParser`, `EUParser`, and `ParserRegistry`
- Pure functions and decorators with `age_at`, `@validate_not_future`, and cached `day_of_week`
- Lazy generators for upcoming milestones
- Context manager clock override with `reference_date(...)`
- Repository pattern and dependency injection for SQLite vs in-memory storage
- Command pattern for CLI subcommands
- Formatter strategies for plain text and JSON
- `pathlib`, `tomllib`, pytest fixtures, parametrization, Hypothesis, Ruff, and mypy

## Checks

```powershell
python -m pytest
python -m ruff check .
python -m mypy src
```

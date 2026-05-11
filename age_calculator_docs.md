# Architecture Decision Record

## App 29 — Age Calculator

**Standalone CLI Utility Group | Document 1 of 5**  
**Status: Accepted**

## Title

Use a layered, stdlib-first Python CLI architecture for age calculation, milestone generation, and saved profile workflows.

## Date

2026-05-09

## Context

Age Calculator is a feature-rich command-line application that calculates calendar age, compares ages, generates future milestones, and stores named profiles. The project is intentionally more than a one-file date script: it demonstrates Python fundamentals, object-oriented design, testing habits, and a beginner-friendly system architecture. The repository describes the system as a layered application where the CLI parses arguments, command objects coordinate workflows, application services call pure domain functions, repositories hide persistence, and formatter strategies control output.

The core problem is deceptively simple: “calculate age.” A naïve solution could subtract two years or divide elapsed days by 365. That would fail for leap years, month/day boundaries, ambiguous date formats, saved profiles, testability, and future expansion. This application instead treats age calculation as a small but real software system with distinct boundaries:

- **Domain layer:** immutable `Age` and `Profile` objects.
- **Calculation layer:** pure age math, milestone generation, leap-year handling, cached weekday lookup, and deterministic clock override.
- **Parsing layer:** date parser strategies with ambiguity detection.
- **Factory layer:** `functools.singledispatch` support for strings, dates, datetimes, and tuples.
- **Service layer:** use-case coordination for one-off calculations and saved profiles.
- **Persistence layer:** a repository interface with SQLite and in-memory implementations.
- **Interface layer:** argparse CLI commands and output formatter strategies.

The application is packaged as `age-calculator`, requires Python 3.11 or newer, has no runtime third-party dependencies, and exposes the installed console script `agecalc`.

## Decision Drivers

- **Calendar correctness over shortcut math.** The app must calculate human-readable years, months, and days rather than approximating age by elapsed days alone.
- **Layered learning value.** The project should demonstrate architecture concepts without becoming too large for an academic CLI portfolio.
- **Stdlib-first runtime.** Date handling, TOML config reading, SQLite persistence, argparse parsing, JSON output, and typing are all possible with the Python standard library.
- **Testability.** Pure functions, context-managed reference dates, in-memory repositories, and injectable services make testing practical.
- **Extensibility.** New date formats, output formats, repositories, or commands should be possible without rewriting the core date math.
- **CLI usability.** Users should be able to calculate one-off ages or manage saved profiles with simple commands.
- **Safety around ambiguous dates.** Inputs like `03/04/2000` should not be guessed if multiple enabled formats interpret them differently.
- **Portfolio evidence.** The code should show dataclasses, protocols, abstract base classes, singledispatch, decorators, generators, context managers, caching, SQLite, argparse, pathlib, and structured exceptions.

## Options Considered

### Option 1 — Single script with direct date subtraction

**Description:** Put all behavior in one `main.py`, parse dates directly, subtract years, and print a string.

**Chosen / Rejected:** Rejected.

**Reason:** This would be fast to build but would not demonstrate layered design, testing seams, profile persistence, parser strategies, or reusable domain functions. It also makes leap-year and ambiguous-date handling easier to get wrong.

### Option 2 — Runtime dependency on a date library

**Description:** Use a third-party package such as `dateutil` to calculate deltas and handle more date formats.

**Chosen / Rejected:** Rejected for this app.

**Reason:** The learning goal is to implement the core calendar logic directly. Adding a dependency would reduce the amount of domain reasoning shown by the project. The current runtime dependency list is intentionally empty.

### Option 3 — Click or Typer CLI

**Description:** Use a third-party CLI framework.

**Chosen / Rejected:** Rejected.

**Reason:** `argparse` is sufficient for the command structure and keeps the runtime dependency-free. The command-object layer already prevents the CLI from becoming a monolithic parser function.

### Option 4 — JSON-only profile store

**Description:** Store profile data as a local JSON file.

**Chosen / Rejected:** Rejected.

**Reason:** JSON would be simpler, but SQLite demonstrates a realistic persistence boundary, schema creation, case-insensitive lookups, upserts, and ordered queries. It also avoids full-file rewrites for every profile update.

### Option 5 — SQLite repository behind an abstract interface

**Description:** Use `ProfileRepository` as an abstract boundary with `SQLiteProfileRepository` for real storage and `InMemoryProfileRepository` for tests.

**Chosen / Rejected:** Chosen.

**Reason:** This gives the app realistic persistence while preserving fast tests and clear dependency injection. It also keeps services independent of SQLite details.

### Option 6 — Parser strategy registry

**Description:** Represent ISO, US, and EU date formats as parser strategies, then let a registry try them in preference order while detecting conflicting interpretations.

**Chosen / Rejected:** Chosen.

**Reason:** Date parsing is a domain risk. A strategy registry makes supported formats explicit and prevents ambiguity from being silently accepted.

### Option 7 — Command objects plus service layer

**Description:** Build a CLI parser, then dispatch to command classes that use services and formatters.

**Chosen / Rejected:** Chosen.

**Reason:** This keeps the CLI from owning business logic. Commands remain small and testable, while services become the main use-case boundary.

## Decision

Age Calculator will be implemented as a small layered Python package under `src/agecalc`. The package will expose a public API for reusable domain operations and an `agecalc` CLI for interactive use.

The accepted design is:

1. Use immutable dataclasses for domain values:
   - `Age`
   - `Profile`

2. Keep age and milestone math pure:
   - `age_at`
   - `milestones`
   - `day_of_week`
   - `reference_date`

3. Use parser strategies for date interpretation:
   - `ISOParser`
   - `USParser`
   - `EUParser`
   - `ParserRegistry`

4. Use `functools.singledispatch` for flexible age creation:
   - string input
   - `date`
   - `datetime`
   - `(year, month, day)` tuple

5. Use service classes to coordinate application workflows:
   - `AgeService`
   - `ProfileService`

6. Use a repository abstraction for saved profiles:
   - `ProfileRepository`
   - `SQLiteProfileRepository`
   - `InMemoryProfileRepository`

7. Use formatter strategies for output:
   - `PlainFormatter`
   - `JSONFormatter`

8. Use argparse command objects for the CLI:
   - `age`
   - `diff`
   - `milestones`
   - `profile add`
   - `profile list`
   - `profile get`
   - `profile delete`
   - `profile age`
   - `profile milestones`

## Rationale

The design is deliberately more structured than a minimal calculator because the app is part of an academic software architecture portfolio. A layered structure proves that the author understands boundaries between parsing, domain logic, persistence, formatting, and command dispatch.

The domain layer is immutable so that calculated ages and saved profiles are safe to pass around without accidental mutation. `Age` stores both calendar components and total seconds. Calendar fields support human output, while `total_seconds` supports ordering, equality, and subtraction.

The calculation layer uses pure functions because date math should be deterministic. The `reference_date` context manager uses a `ContextVar`, which lets tests or library callers override “today” without changing global module state for the whole process.

The parser layer protects user intent. ISO, US, and EU dates are all supported, but ambiguity is treated as an error rather than a guess. This is a strong design choice for a CLI tool because it avoids silently producing a wrong age.

The service layer is intentionally thin. It does not hide the domain; it coordinates it. `AgeService` handles one-off age use cases, and `ProfileService` handles saved-profile workflows. This prevents the CLI from knowing whether a profile is stored in SQLite or memory.

The repository interface makes persistence replaceable. SQLite is useful for real CLI usage, but `InMemoryProfileRepository` supports tests and examples without touching disk.

The formatter layer means output concerns stay outside the calculation and service layers. Plain text is suitable for humans, while JSON is suitable for scripts.

## Trade-offs Accepted

- **More files than a beginner script.** The project uses multiple modules for a simple domain. This is acceptable because the goal is architecture practice.
- **No third-party date library.** The app owns leap-day and month-boundary logic, which increases responsibility but improves learning value.
- **SQLite over JSON.** SQLite adds schema and connection management complexity but gives a more realistic repository example.
- **Argparse verbosity.** `argparse` requires more boilerplate than Typer or Click, but avoids runtime dependencies.
- **Limited date format scope.** Only ISO, US, and EU formats are supported. Natural language dates are intentionally out of scope.
- **Ambiguous date rejection.** Some user inputs that “could work” are rejected because correctness is prioritized over convenience.
- **No concurrent database coordination.** SQLite is suitable for local CLI use, but the design is not intended for heavy concurrent writes.
- **Minimal config validation.** Config values are read from TOML with defaults, but the config layer does not implement a full schema system.
- **No graphical interface.** The app is CLI-first and API-friendly, not a desktop or web app.

## Consequences

### Positive consequences

- The app is easy to explain as a layered system.
- Core date math can be tested without CLI or database setup.
- The profile system can use SQLite in production and memory in tests.
- CLI output can be switched between plain text and JSON without changing services.
- Date parsing is explicit and safer than informal string handling.
- The project demonstrates a wide range of Python fundamentals in a coherent app.

### Negative consequences

- Developers must understand several layers before making changes.
- Small feature changes may require touching parser, service, formatter, CLI, and tests.
- SQLite schema evolution is not yet versioned.
- The date parser can reject inputs that users might expect to parse.
- Some behaviors, such as timezone-based default reference dates, depend on local environment data.

## Superseded By

Not superseded.

A future version could supersede this ADR if the app becomes a larger personal-data tool with profile import/export, database migrations, richer calendar rules, or a GUI/web interface.

---

# Technical Design Document

## App 29 — Age Calculator

**Standalone CLI Utility Group | Document 2 of 5**

## Purpose & Scope

Age Calculator is a Python 3.11+ CLI package for calculating ages, age differences, future milestones, and saved profile ages. It is designed as a small layered application that demonstrates clean separation between command parsing, application services, domain logic, parsing strategies, persistence, and output formatting.

### In scope

- Calculate age from a birthdate.
- Calculate difference between two ages.
- Generate upcoming birthday and day-count milestones.
- Read dates in ISO, US, and EU formats.
- Reject ambiguous date inputs.
- Support explicit reference dates.
- Support timezone-based default reference date.
- Save, retrieve, list, delete, and calculate age for named profiles.
- Store profiles in SQLite.
- Provide an in-memory repository for tests or dependency injection.
- Output plain text or JSON.
- Read optional TOML config from `~/.agecalc/config.toml`.
- Provide an installed console script named `agecalc`.

### Out of scope

- Natural language date parsing.
- Time-of-day age output.
- Multiple calendar systems.
- GUI, web server, or API server.
- Network sync for profiles.
- Authentication or encrypted profile storage.
- Database migrations beyond initial table creation.
- Multi-user concurrent profile editing.
- Internationalized output strings.

## System Context

The app runs as a local command-line program. A user invokes `agecalc` from a shell. The CLI loads optional config, builds a parser registry and services, dispatches to a command object, formats the result, and prints to stdout.

```text
User shell
  |
  v
agecalc CLI
  |
  +--> config loader (~/.agecalc/config.toml)
  |
  +--> command object
          |
          +--> AgeService
          |      |
          |      +--> ParserRegistry
          |      +--> create_age / age_at / milestones
          |
          +--> ProfileService
                 |
                 +--> ProfileRepository
                        |
                        +--> SQLite database (~/.agecalc/profiles.sqlite3)
```

## Component Breakdown

### `agecalc.__init__`

Public package surface. It exports:

- `Age`
- `Profile`
- `age_at`
- `create_age`
- `milestones`
- `reference_date`

This gives library users a small import surface while keeping internal modules organized.

### `agecalc.domain`

Defines immutable domain objects.

#### `Age`

An immutable dataclass with:

- `years`
- `months`
- `days`
- `total_seconds`

Important behaviors:

- Rejects negative components.
- Provides `total_days`.
- Supports equality and ordering by `total_seconds`.
- Supports subtraction between two `Age` objects.
- Supports custom formatting:
  - default / `ymd`
  - `days`
  - `seconds`

#### `Profile`

An immutable dataclass with:

- `name`
- `birthdate`
- `created_at`

`Profile.create()` trims the name and rejects empty names.

### `agecalc.exceptions`

Defines the application-level exception hierarchy:

```text
AgeCalcError
  ├── InvalidDateError
  │     ├── AmbiguousDateError
  │     └── FutureBirthDateError
  └── UnknownProfileError
```

The CLI catches `AgeCalcError` and exits cleanly with an error message.

### `agecalc.calculations`

Owns pure age math and milestone generation.

Key objects and functions:

- `current_reference_date()`
- `reference_date(value)`
- `validate_not_future`
- `age_at(birthdate, reference)`
- `day_of_week(value)`
- `Milestone`
- `milestones(birthdate, reference, limit)`

Important implementation choices:

- Leap-day birthdays fall back to February 28 in non-leap years.
- Month addition uses `calendar.monthrange()` to avoid overflow.
- Future birthdates raise `FutureBirthDateError`.
- `day_of_week` uses `lru_cache(maxsize=2048)`.
- Milestones are lazily merged from multiple streams with `heapq`.

### `agecalc.parsing`

Defines the date parsing strategy layer.

Components:

- `DateParser` protocol
- `ISOParser`
- `USParser`
- `EUParser`
- `ParserRegistry`
- `default_registry(preferred="iso")`

The registry tries all configured parsers and gathers successful matches. If no parser succeeds, it raises `InvalidDateError`. If multiple parsers produce different valid dates, it raises `AmbiguousDateError`.

### `agecalc.factory`

Defines `create_age` with `functools.singledispatch`.

Supported inputs:

- `str`
- `date`
- `datetime`
- `tuple[Any, ...]` in `(year, month, day)` form

It also provides `normalize_birthdate()`, which converts supported inputs into a `date` without calculating age. Services use this when they need the birthdate itself, such as for profile storage or milestone generation.

### `agecalc.config`

Loads optional TOML configuration from `~/.agecalc/config.toml`.

Config fields:

- `preferred_date_format`
- `output_format`
- `reference_timezone`
- `database_path`

If the config file is missing, default values are used. Timezone lookup uses `zoneinfo`; if the configured timezone is not available, the app falls back to UTC for `today_in_timezone`.

### `agecalc.storage`

Defines persistence.

#### `ProfileRepository`

Abstract repository interface:

- `save(profile)`
- `get(name)`
- `list()`
- `delete(name)`

#### `InMemoryProfileRepository`

Stores profiles in a dictionary keyed by case-folded name. Useful for tests and dependency injection.

#### `SQLiteProfileRepository`

Stores profiles in SQLite. It creates the parent directory and ensures a `profiles` table exists.

Table fields:

- `name TEXT PRIMARY KEY`
- `birthdate TEXT NOT NULL`
- `created_at TEXT NOT NULL`

It supports:

- upsert on save
- case-insensitive lookup
- ordered listing
- delete with missing-profile detection

### `agecalc.services`

Defines application services.

#### `AgeService`

Coordinates one-off calculation use cases:

- `calculate(value, reference)`
- `difference(left, right, reference)`
- `upcoming_milestones(value, reference, limit)`

#### `ProfileService`

Coordinates saved-profile use cases:

- `add(name, birthdate_value)`
- `get(name)`
- `list_profiles()`
- `delete(name)`
- `age_for(name, reference)`
- `milestones_for(name, reference, limit)`

Services depend on parser registry and repository abstractions, not on CLI details.

### `agecalc.formatters`

Defines output strategies.

#### `PlainFormatter`

Produces human-readable text:

- `Age: ...`
- `Difference: ...`
- `Upcoming milestones: ...`
- `No profiles saved.`

#### `JSONFormatter`

Produces structured JSON for scripting.

Formatter functions convert `Age`, `Milestone`, and `Profile` into dictionaries before serializing.

### `agecalc.cli`

Owns command-line parsing and command dispatch.

Key structures:

- `Command` protocol
- `CommandContext`
- Command classes such as `AgeCommand`, `DiffCommand`, and profile commands
- `COMMANDS` dispatch map
- `build_parser(config)`
- `_build_context(args, config, repository)`
- `main(argv=None, repository=None)`

The CLI loads config, parses args, builds services and formatters, executes a command object, prints output, catches `AgeCalcError`, and returns an exit code.

## Module Dependency Graph

```text
agecalc.cli
  ├── agecalc.config
  ├── agecalc.exceptions
  ├── agecalc.formatters
  ├── agecalc.parsing
  ├── agecalc.services
  └── agecalc.storage

agecalc.services
  ├── agecalc.calculations
  ├── agecalc.domain
  ├── agecalc.factory
  ├── agecalc.parsing
  └── agecalc.storage

agecalc.factory
  ├── agecalc.calculations
  ├── agecalc.domain
  ├── agecalc.exceptions
  └── agecalc.parsing

agecalc.calculations
  ├── agecalc.domain
  └── agecalc.exceptions

agecalc.storage
  ├── agecalc.domain
  └── agecalc.exceptions

agecalc.formatters
  ├── agecalc.calculations
  └── agecalc.domain

agecalc.config
  └── stdlib: pathlib, tomllib, zoneinfo
```

## Core Algorithms & Logic

### Calendar age calculation

`age_at()` calculates age in years, months, and days.

Algorithm:

1. Resolve reference date.
2. Reject future birthdates.
3. Compute tentative year difference.
4. Build birthday anniversary in the reference year.
5. If anniversary is after reference, subtract one year.
6. Walk month-by-month from the last anniversary until adding another month would exceed reference.
7. Remaining difference in days becomes the `days` component.
8. Total elapsed days times seconds-per-day becomes `total_seconds`.

Leap-day handling:

- `_birthday_in_year()` attempts `birthdate.replace(year=year)`.
- If that fails, the date is February 29 in a non-leap year.
- The birthday is treated as February 28 for that year.

### Month addition

`_add_months()` computes year/month rollover manually, then clamps the day to the last valid day in the target month. This prevents invalid dates like April 31.

### Future-date validation

`validate_not_future` is a decorator that wraps functions whose first argument is a birthdate. It compares the birthdate to the resolved reference date and raises `FutureBirthDateError` if the birthdate is later.

### Reference-date override

`reference_date(value)` uses a `ContextVar` token to temporarily override the current reference date. This gives deterministic tests without making the whole module depend on a mutable global.

### Milestone generation

`milestones()` merges two infinite lazy streams:

- birthday milestones
- day-count milestones in 1,000-day increments

It uses a heap keyed by target date. Each time it yields the next milestone, it pulls the next value from that stream and pushes it back onto the heap. This keeps output ordered while preserving laziness.

### Date parsing and ambiguity detection

`ParserRegistry.parse()`:

1. Strips input.
2. Tries each parser.
3. Collects successful parser results.
4. If there are no matches, raises `InvalidDateError`.
5. If successful parsers produce more than one unique date, raises `AmbiguousDateError`.
6. Otherwise returns the single unique date.

This prevents the app from guessing between US and EU interpretations.

### Single-dispatch age creation

`create_age` uses `functools.singledispatch`:

- `str` input goes through the parser registry.
- `date` input goes directly to `age_at`.
- `datetime` input uses `.date()`.
- `tuple` input must have exactly three components and is converted to `date(year, month, day)`.

Unsupported input types raise `InvalidDateError`.

### Repository storage

`SQLiteProfileRepository` ensures a table exists during initialization. `save()` uses SQLite `ON CONFLICT(name) DO UPDATE` so profile add acts as add-or-update. `get()` and `delete()` use `lower(name) = lower(?)` for case-insensitive matching.

### Command dispatch

The CLI assigns each parser branch a `command_name`, then uses a `COMMANDS` dictionary to construct the matching command object. Command classes return formatted strings rather than printing directly. `main()` owns printing and exit codes.

## Data Structures

### `Age`

```python
Age(
    years: int,
    months: int,
    days: int,
    total_seconds: int,
)
```

### `Profile`

```python
Profile(
    name: str,
    birthdate: date,
    created_at: datetime,
)
```

### `Milestone`

```python
Milestone(
    label: str,
    target_date: date,
    days_until: int,
    weekday: str,
)
```

### Config

```python
Config(
    preferred_date_format: str = "iso",
    output_format: str = "plain",
    reference_timezone: str = "UTC",
    database_path: Path = Path.home() / ".agecalc" / "profiles.sqlite3",
)
```

### SQLite row

```text
profiles
  name TEXT PRIMARY KEY
  birthdate TEXT NOT NULL
  created_at TEXT NOT NULL
```

### JSON age output

```json
{
  "age": {
    "years": 25,
    "months": 0,
    "days": 0,
    "total_days": 9131,
    "total_seconds": 788918400
  }
}
```

### JSON milestones output

```json
{
  "milestones": [
    {
      "label": "10,000 days old",
      "target_date": "2027-11-27",
      "days_until": 501,
      "weekday": "Saturday"
    }
  ]
}
```

## State Management

### Stateless calculations

Core age calculation and milestone generation are stateless except for cached weekday results and the optional `ContextVar` reference-date override.

### Config state

Configuration is read from `~/.agecalc/config.toml` if present. The config object is immutable and passed through the command context.

### Profile state

Saved profiles are persisted to SQLite at the configured database path. The default is:

```text
~/.agecalc/profiles.sqlite3
```

### Runtime command context

`CommandContext` holds the active configuration, formatter, services, and parser registry for one CLI invocation. It prevents each command class from rebuilding dependencies.

### Cache state

`day_of_week` uses an LRU cache with a maximum size of 2048 entries.

## Error Handling Strategy

### Domain/application errors

All expected application errors inherit from `AgeCalcError`. The CLI catches these and prints:

```text
error: <message>
```

Then it returns exit code `2`.

### Date errors

- Invalid date text raises `InvalidDateError`.
- Ambiguous date text raises `AmbiguousDateError`.
- Birthdates after reference date raise `FutureBirthDateError`.

### Profile errors

Missing profiles raise `UnknownProfileError`.

### Argparse errors

Invalid command syntax, invalid choices, or non-positive milestone limits are handled by argparse and normally exit with code `2`.

### SQLite/system errors

SQLite or filesystem errors are not wrapped as `AgeCalcError` in the inspected code. They may surface as Python exceptions unless they occur in paths explicitly guarded by application exceptions. This is acceptable for a learning project but is a candidate for future hardening.

## External Dependencies

### Runtime dependencies

None outside the Python standard library.

Runtime stdlib modules include:

| Module | Purpose |
|---|---|
| `argparse` | CLI parsing |
| `calendar` | Month length calculation |
| `contextlib` | Reference date context manager |
| `contextvars` | Context-local reference date |
| `dataclasses` | Immutable domain records |
| `datetime` | Date and time operations |
| `functools` | `singledispatch`, `lru_cache`, `total_ordering`, wraps |
| `heapq` | Milestone stream merging |
| `itertools` | Tie-breaking sequence counter |
| `json` | JSON output |
| `pathlib` | Config and database paths |
| `sqlite3` | Profile persistence |
| `tomllib` | TOML config parsing |
| `zoneinfo` | Timezone-aware default reference date |

### Development dependencies

| Dependency | Version constraint | Purpose |
|---|---:|---|
| `pytest` | `>=8.0` | Test runner |
| `hypothesis` | `>=6.100` | Property-based tests |
| `ruff` | `>=0.5` | Linting |
| `mypy` | `>=1.8` | Static type checking |

## Concurrency Model

The application is synchronous and single-process.

There is no threading, async IO, background scheduler, or long-running service. Each CLI invocation performs one command and exits.

SQLite handles basic local file locking, but the app is not designed for multiple simultaneous profile-writing processes. Concurrent use could be improved later with clearer database error handling and transaction guidance.

## Known Limitations

- Only three input date formats are supported.
- Ambiguous dates are rejected instead of prompting interactively.
- Leap-day birthdays are treated as February 28 in non-leap years.
- Calendar calculations ignore time-of-day.
- Profile storage is local only.
- No database migration/version table exists.
- Config values are lightly normalized but not schema-validated.
- CLI catches `AgeCalcError` but not every possible storage or OS exception.
- The JSON output shape is stable enough for scripts but not explicitly versioned.
- No direct test files were available during this documentation pass; verification is documented from repository configuration and inspected behavior.

## Design Patterns Used

| Pattern | Where | Why |
|---|---|---|
| Layered architecture | CLI → commands → services → domain/storage | Keeps responsibilities separate |
| Strategy | Date parsers and output formatters | Makes parsing/output replaceable |
| Repository | `ProfileRepository` | Hides persistence details |
| Dependency injection | Services accept registry/repository | Enables tests and alternate storage |
| Command | CLI command classes | Keeps parser from owning behavior |
| Factory | `create_age` singledispatch | Normalizes several input types |
| Decorator | `validate_not_future` | Centralizes date safety check |
| Context manager | `reference_date` | Deterministic temporary clock override |
| Lazy generator | Milestone streams | Efficient chronological milestone generation |
| Value object | `Age`, `Milestone` | Clear immutable domain records |

---

# Interface Design Specification

## App 29 — Age Calculator

**Standalone CLI Utility Group | Document 3 of 5**

## Invocation Syntax

### Installed command

```bash
agecalc [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

### Module invocation

The project exposes the console script `agecalc = "agecalc.cli:main"`. Direct module execution is not documented as a primary interface.

### Install for local development

```bash
python -m pip install -e .[dev]
```

### Main commands

```bash
agecalc age BIRTHDATE [--reference DATE] [--format plain|json]
agecalc diff LEFT RIGHT [--reference DATE] [--format plain|json]
agecalc milestones BIRTHDATE [--reference DATE] [--limit N] [--format plain|json]

agecalc profile add NAME BIRTHDATE [--format plain|json]
agecalc profile list [--format plain|json]
agecalc profile get NAME [--format plain|json]
agecalc profile delete NAME [--format plain|json]
agecalc profile age NAME [--reference DATE] [--format plain|json]
agecalc profile milestones NAME [--reference DATE] [--limit N] [--format plain|json]
```

The `--format` option can be passed globally or after a subcommand.

## Argument Reference Table

### Global options

| Name | Type | Required | Default | Valid values | Description |
|---|---|---:|---|---|---|
| `--format` | string | No | `output_format` from config, otherwise `plain` | `plain`, `json` | Selects output formatter. Can also be supplied on subcommands. |
| `-h`, `--help` | flag | No | N/A | N/A | Shows help and exits. |

### `age` command

| Name | Type | Required | Default | Valid values | Description |
|---|---|---:|---|---|---|
| `birthdate` | string | Yes | N/A | ISO, US, or EU date | Birthdate to calculate from. |
| `--reference`, `-r` | string | No | Today in configured timezone | ISO, US, or EU date | Date at which to calculate age. |
| `--format` | string | No | inherited/global/config | `plain`, `json` | Output format for this command. |

### `diff` command

| Name | Type | Required | Default | Valid values | Description |
|---|---|---:|---|---|---|
| `left` | string | Yes | N/A | ISO, US, or EU date | First birthdate. |
| `right` | string | Yes | N/A | ISO, US, or EU date | Second birthdate. |
| `--reference`, `-r` | string | No | Today in configured timezone | ISO, US, or EU date | Reference date for both ages. |
| `--format` | string | No | inherited/global/config | `plain`, `json` | Output format for this command. |

### `milestones` command

| Name | Type | Required | Default | Valid values | Description |
|---|---|---:|---|---|---|
| `birthdate` | string | Yes | N/A | ISO, US, or EU date | Birthdate for milestone generation. |
| `--reference`, `-r` | string | No | Today in configured timezone | ISO, US, or EU date | Date from which upcoming milestones are calculated. |
| `--limit` | integer | No | `10` | `>= 1` | Maximum number of milestones to show. |
| `--format` | string | No | inherited/global/config | `plain`, `json` | Output format for this command. |

### `profile add`

| Name | Type | Required | Default | Valid values | Description |
|---|---|---:|---|---|---|
| `name` | string | Yes | N/A | non-empty after trimming | Profile display name. Existing name is updated. |
| `birthdate` | string | Yes | N/A | ISO, US, or EU date | Profile birthdate. |
| `--format` | string | No | inherited/global/config | `plain`, `json` | Output format for this command. |

### `profile list`

| Name | Type | Required | Default | Valid values | Description |
|---|---|---:|---|---|---|
| `--format` | string | No | inherited/global/config | `plain`, `json` | Output format for this command. |

### `profile get`

| Name | Type | Required | Default | Valid values | Description |
|---|---|---:|---|---|---|
| `name` | string | Yes | N/A | saved profile name | Profile to retrieve. |
| `--format` | string | No | inherited/global/config | `plain`, `json` | Output format for this command. |

### `profile delete`

| Name | Type | Required | Default | Valid values | Description |
|---|---|---:|---|---|---|
| `name` | string | Yes | N/A | saved profile name | Profile to delete. |
| `--format` | string | No | inherited/global/config | `plain`, `json` | Output format for confirmation message. |

### `profile age`

| Name | Type | Required | Default | Valid values | Description |
|---|---|---:|---|---|---|
| `name` | string | Yes | N/A | saved profile name | Profile whose age should be calculated. |
| `--reference`, `-r` | string | No | Today in configured timezone | ISO, US, or EU date | Reference date. |
| `--format` | string | No | inherited/global/config | `plain`, `json` | Output format. |

### `profile milestones`

| Name | Type | Required | Default | Valid values | Description |
|---|---|---:|---|---|---|
| `name` | string | Yes | N/A | saved profile name | Profile whose milestones should be calculated. |
| `--reference`, `-r` | string | No | Today in configured timezone | ISO, US, or EU date | Reference date. |
| `--limit` | integer | No | `10` | `>= 1` | Maximum number of milestones. |
| `--format` | string | No | inherited/global/config | `plain`, `json` | Output format. |

## Input Contract

### Date formats

Supported date inputs:

| Name | Pattern | Example |
|---|---|---|
| ISO | `YYYY-MM-DD` | `2000-02-29` |
| US | `MM/DD/YYYY` | `12/31/2000` |
| EU | `DD/MM/YYYY` | `31/12/2000` |

The parser tries configured strategies and rejects ambiguous inputs where different formats produce different valid dates.

Example ambiguous input:

```text
03/04/2000
```

This can mean March 4 or April 3 depending on US/EU interpretation, so the app raises an ambiguity error.

### Birthdate rules

- Must parse into a valid date.
- Must not be after the reference date.
- May be a leap-day date.
- Future birthdates are rejected.

### Reference date rules

- Optional.
- If absent, defaults to today in `reference_timezone`.
- If present, uses the same parser registry as birthdates.
- Must parse into a valid date.

### Profile name rules

- Trimmed by `Profile.create`.
- Must not be empty after trimming.
- Lookups are case-insensitive in both SQLite and in-memory repositories.

### Config contract

Optional file:

```text
~/.agecalc/config.toml
```

Supported keys:

```toml
preferred_date_format = "iso"
output_format = "plain"
reference_timezone = "America/Los_Angeles"
database_path = "~/.agecalc/profiles.sqlite3"
```

Invalid TOML may raise a parse error. Unknown keys are ignored by the inspected config loader.

## Output Contract

### Plain age output

```text
Age: 25 years, 0 months, 0 days (9131 days, 788918400 seconds)
```

### JSON age output

```json
{
  "age": {
    "years": 25,
    "months": 0,
    "days": 0,
    "total_days": 9131,
    "total_seconds": 788918400
  }
}
```

### Plain difference output

```text
Difference: 2 years, 3 months, 5 days (825 days)
```

### Plain milestones output

```text
Upcoming milestones:
- 30th birthday: 2030-07-12 (Friday, in 1445 days)
- 12,000 days old: 2031-05-03 (Saturday, in 1740 days)
```

### JSON milestones output

```json
{
  "milestones": [
    {
      "label": "30th birthday",
      "target_date": "2030-07-12",
      "days_until": 1445,
      "weekday": "Friday"
    }
  ]
}
```

### Plain profile output

```text
Ada: born 1815-12-10
```

### Empty profile list output

```text
No profiles saved.
```

### JSON profile list output

```json
{
  "profiles": [
    {
      "name": "Ada",
      "birthdate": "1815-12-10",
      "created_at": "2026-05-09T12:00:00+00:00"
    }
  ]
}
```

### Delete output

Plain:

```text
Deleted profile 'Ada'.
```

JSON:

```json
{
  "message": "Deleted profile 'Ada'."
}
```

## Exit Code Reference

| Exit code | Meaning | Source |
|---:|---|---|
| `0` | Command succeeded | `main()` returns success |
| `2` | Application-level error such as invalid date, future birthdate, ambiguous date, missing profile | `AgeCalcError` handling |
| `2` | CLI syntax/argument error | argparse behavior |
| non-zero / traceback possible | Unexpected storage, OS, SQLite, or TOML error not wrapped as `AgeCalcError` | Python runtime behavior |

## Error Output Behavior

Application errors are printed to stderr:

```text
error: Birthdate 2030-01-01 is after reference date 2026-05-09.
```

Argparse errors are printed in argparse’s standard format, usually including usage text.

Examples:

```text
agecalc: error: argument --format: invalid choice: 'xml' (choose from 'plain', 'json')
```

```text
agecalc milestones: error: argument --limit: '0' must be at least 1.
```

## Environment Variables

No app-specific environment variables are read directly by the inspected code.

Environment-dependent behavior:

| Environment factor | Effect |
|---|---|
| User home directory | Determines default `~/.agecalc/config.toml` and `~/.agecalc/profiles.sqlite3` paths. |
| System timezone database | Required by `zoneinfo` for named timezones. If lookup fails, the app falls back to UTC for default reference-date calculation. |

## Configuration Files

### Default config path

```text
~/.agecalc/config.toml
```

### Example config

```toml
preferred_date_format = "iso"
output_format = "plain"
reference_timezone = "America/Los_Angeles"
database_path = "~/.agecalc/profiles.sqlite3"
```

### Config fields

| Field | Type | Default | Description |
|---|---|---|---|
| `preferred_date_format` | string | `iso` | Parser strategy preferred first. Valid intended values are `iso`, `us`, `eu`. |
| `output_format` | string | `plain` | Default CLI output format. Valid CLI values are `plain`, `json`. |
| `reference_timezone` | string | `UTC` | Timezone used for default “today.” |
| `database_path` | string/path | `~/.agecalc/profiles.sqlite3` | SQLite profile database path. |

## Side Effects

| Command | Side effects |
|---|---|
| `age` | No filesystem writes. |
| `diff` | No filesystem writes. |
| `milestones` | No filesystem writes. |
| `profile add` | Creates parent directory and SQLite database if needed; inserts or updates a profile. |
| `profile list` | Reads SQLite database; database initialization may create schema if repository is constructed. |
| `profile get` | Reads SQLite database. |
| `profile delete` | Deletes a row from SQLite database. |
| `profile age` | Reads SQLite database. |
| `profile milestones` | Reads SQLite database. |

## Usage Examples

### Basic age calculation

```bash
agecalc age 2000-02-29 --reference 2025-02-28
```

Expected plain output shape:

```text
Age: 25 years, 0 months, 0 days (... days, ... seconds)
```

### JSON milestone output

```bash
agecalc --format json milestones 1998-07-12 --limit 3
```

Expected output shape:

```json
{
  "milestones": [
    {
      "label": "...",
      "target_date": "...",
      "days_until": 0,
      "weekday": "..."
    }
  ]
}
```

### Subcommand-local output format

```bash
agecalc milestones 1998-07-12 --limit 3 --format json
```

This is equivalent to passing `--format json` globally.

### Saved profile workflow

```bash
agecalc profile add Ada 1815-12-10
agecalc profile age Ada --reference 1852-11-27
agecalc profile list
```

### Profile milestones

```bash
agecalc profile milestones Ada --reference 1852-11-27 --limit 5
```

### Age difference

```bash
agecalc diff 1998-07-12 2000-02-29 --reference 2026-05-09
```

### Intentional failure: ambiguous date

```bash
agecalc age 03/04/2000 --reference 2026-05-09
```

Expected error behavior:

```text
error: Ambiguous date '03/04/2000'; possible interpretations: ...
```

### Intentional failure: future birthdate

```bash
agecalc age 2099-01-01 --reference 2026-05-09
```

Expected error behavior:

```text
error: Birthdate 2099-01-01 is after reference date 2026-05-09.
```

### Intentional failure: invalid limit

```bash
agecalc milestones 1998-07-12 --limit 0
```

Expected argparse error:

```text
agecalc milestones: error: argument --limit: '0' must be at least 1.
```

---

# Runbook

## App 29 — Age Calculator

**Standalone CLI Utility Group | Document 4 of 5**

## Prerequisites

- Python 3.11 or newer.
- A shell environment capable of running Python commands.
- `pip` for editable install.
- Optional development tools:
  - `pytest`
  - `hypothesis`
  - `ruff`
  - `mypy`

The runtime application itself uses only the Python standard library.

## Installation Procedure

### 1. Clone or enter the repository

```bash
cd Age-Calculator
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install editable package with dev dependencies

```bash
python -m pip install -e .[dev]
```

### 4. Verify the command is available

```bash
agecalc --help
```

Expected result:

- CLI help text prints.
- Exit code is `0`.

## Configuration Steps

### Optional config directory

The app reads:

```text
~/.agecalc/config.toml
```

The directory does not need to exist for one-off calculations. It will be created automatically when profile database storage is initialized.

### Example config

```toml
preferred_date_format = "iso"
output_format = "plain"
reference_timezone = "America/Los_Angeles"
database_path = "~/.agecalc/profiles.sqlite3"
```

### Recommended student/dev config

For repeatable local testing, keep the default config absent or set:

```toml
preferred_date_format = "iso"
output_format = "plain"
reference_timezone = "UTC"
database_path = "~/.agecalc/profiles.sqlite3"
```

This avoids surprises from local timezone changes.

## Standard Operating Procedures

### Calculate a one-off age

```bash
agecalc age 2000-02-29 --reference 2025-02-28
```

### Generate milestones

```bash
agecalc milestones 1998-07-12 --limit 5
```

### Use JSON output

```bash
agecalc --format json age 2000-02-29 --reference 2025-02-28
```

### Add a profile

```bash
agecalc profile add Ada 1815-12-10
```

### Calculate age for a profile

```bash
agecalc profile age Ada --reference 1852-11-27
```

### List profiles

```bash
agecalc profile list
```

### Delete a profile

```bash
agecalc profile delete Ada
```

### Run verification checks

```bash
python -m pytest
python -m ruff check .
python -m mypy src
```

## Health Checks

### CLI availability

```bash
agecalc --help
```

Pass criteria:

- Command exists.
- Help text prints.
- No import traceback.

### Package import

```bash
python - <<'PY'
from agecalc import Age, age_at
from datetime import date
print(age_at(date(2000, 1, 1), date(2020, 1, 1)))
PY
```

Pass criteria:

- Import succeeds.
- Output contains an `Age(...)` representation or formatted object.

### One-off calculation

```bash
agecalc age 2000-01-01 --reference 2020-01-01
```

Pass criteria:

- Output starts with `Age:`.
- Output includes years, months, days, days total, and seconds total.

### Ambiguous date guard

```bash
agecalc age 03/04/2000 --reference 2020-01-01
```

Pass criteria:

- Command exits with non-zero status.
- Error mentions ambiguity.

### Profile database write/read

```bash
agecalc profile add TestUser 2000-01-01
agecalc profile get TestUser
```

Pass criteria:

- Add command prints saved profile.
- Get command prints the same birthdate.
- SQLite database exists at configured path.

### JSON output

```bash
agecalc --format json age 2000-01-01 --reference 2020-01-01
```

Pass criteria:

- Output is valid JSON.
- Top-level key is `age`.

## Expected Output Samples

### Plain age

```text
Age: 20 years, 0 months, 0 days (7305 days, 631152000 seconds)
```

Exact totals depend on date inputs and leap years.

### Plain milestones

```text
Upcoming milestones:
- 30th birthday: 2028-07-12 (Wednesday, in 794 days)
- 11,000 days old: 2028-08-28 (Monday, in 841 days)
```

### JSON profile

```json
{
  "profile": {
    "name": "Ada",
    "birthdate": "1815-12-10",
    "created_at": "2026-05-09T12:00:00+00:00"
  }
}
```

### Empty profile list

```text
No profiles saved.
```

## Known Failure Modes

### Command not found

Symptom:

```text
agecalc: command not found
```

Likely causes:

- Editable install was not run.
- Virtual environment is not active.
- Shell PATH does not include environment scripts directory.

Recovery:

```bash
python -m pip install -e .[dev]
python -m agecalc.cli --help
```

Note: direct module execution is not the documented interface, but importing the CLI module can help diagnose install issues.

### Invalid date

Symptom:

```text
error: Could not parse '...' as ISO, US, or EU date.
```

Cause:

- Unsupported format.
- Invalid calendar date.
- Typo.

Recovery:

Use one of:

```text
YYYY-MM-DD
MM/DD/YYYY
DD/MM/YYYY
```

### Ambiguous date

Symptom:

```text
error: Ambiguous date '03/04/2000'; possible interpretations: ...
```

Cause:

- Date can be interpreted differently by multiple parser strategies.

Recovery:

Use ISO format:

```bash
agecalc age 2000-03-04
```

### Future birthdate

Symptom:

```text
error: Birthdate ... is after reference date ...
```

Cause:

- Birthdate is later than the selected reference date.

Recovery:

- Fix the birthdate.
- Pass a later `--reference` only if that is intentional.

### Profile not found

Symptom:

```text
error: No profile named 'Ada'.
```

Cause:

- Profile has not been saved.
- Name typo.
- Different database path configured.

Recovery:

```bash
agecalc profile list
agecalc profile add Ada 1815-12-10
```

### SQLite database path issue

Symptom:

- Permission error.
- Directory creation failure.
- SQLite operational error.

Likely causes:

- Configured database path is not writable.
- Parent directory cannot be created.
- File is locked or corrupted.

Recovery:

1. Check config:
   ```bash
   cat ~/.agecalc/config.toml
   ```
2. Use a writable path:
   ```toml
   database_path = "~/.agecalc/profiles.sqlite3"
   ```
3. Move aside a corrupt database:
   ```bash
   mv ~/.agecalc/profiles.sqlite3 ~/.agecalc/profiles.sqlite3.bak
   ```

### Timezone fallback

Symptom:

- Default reference date seems to use UTC instead of configured timezone.

Cause:

- `zoneinfo` could not find the named timezone.

Recovery:

- Check spelling, e.g. `America/Los_Angeles`.
- On Windows, install timezone data if needed:
  ```bash
  python -m pip install tzdata
  ```

## Troubleshooting Decision Tree

```text
Command fails?
  |
  +-- "agecalc not found"?
  |     |
  |     +-- Activate venv and reinstall: python -m pip install -e .[dev]
  |
  +-- Argument usage error?
  |     |
  |     +-- Run agecalc --help or agecalc COMMAND --help
  |
  +-- Date parsing error?
  |     |
  |     +-- Use ISO YYYY-MM-DD
  |
  +-- Ambiguous date error?
  |     |
  |     +-- Use ISO YYYY-MM-DD instead of slash format
  |
  +-- Profile missing?
  |     |
  |     +-- Run agecalc profile list
  |     +-- Check ~/.agecalc/config.toml database_path
  |
  +-- SQLite/path error?
  |     |
  |     +-- Confirm database parent directory is writable
  |     +-- Move aside corrupt database file if necessary
  |
  +-- Unexpected traceback?
        |
        +-- Run python -m pytest
        +-- Run python -m ruff check .
        +-- Inspect recent code changes around CLI, config, or storage
```

## Dependency Failure Handling

### Runtime dependencies

The app has no third-party runtime dependencies. If runtime import fails, the likely issue is Python version or editable install path.

### Development dependencies

If `pytest`, `ruff`, `mypy`, or `hypothesis` is missing:

```bash
python -m pip install -e .[dev]
```

or:

```bash
python -m pip install -r requirements.txt
```

### Python version mismatch

Symptom:

- `tomllib` import failure.
- Type syntax failure.
- Package install rejects Python version.

Recovery:

Install Python 3.11+.

## Recovery Procedures

### Reset profile database

Use this only if profile data can be discarded.

```bash
mv ~/.agecalc/profiles.sqlite3 ~/.agecalc/profiles.sqlite3.bak
agecalc profile list
```

The next repository initialization will create a fresh database.

### Restore config defaults

```bash
mv ~/.agecalc/config.toml ~/.agecalc/config.toml.bak
```

Then rerun:

```bash
agecalc age 2000-01-01
```

The app will use default config values.

### Diagnose date parsing

Use explicit ISO dates for both birthdate and reference:

```bash
agecalc age 2000-03-04 --reference 2026-05-09
```

If this works, the previous error was likely date-format ambiguity.

### Diagnose profile path

Run:

```bash
python - <<'PY'
from agecalc.config import load_config
print(load_config())
PY
```

Confirm `database_path` is what you expect.

## Logging Reference

The inspected code does not define a logging system for this app. Operational output is command stdout/stderr.

Recommended diagnostic sources:

| Source | Use |
|---|---|
| stdout | Successful command output |
| stderr | Application and argparse errors |
| SQLite database file | Saved profile state |
| config TOML | User preferences and database path |
| pytest output | Regression verification |

## Maintenance Notes

- Prefer ISO dates in docs and tests.
- Keep date math pure; avoid moving CLI or database behavior into `calculations.py`.
- Add parser strategies only through the `DateParser` protocol and registry.
- Keep services independent of argparse.
- Keep repository behavior behind `ProfileRepository`.
- If JSON output becomes a supported automation contract, version the response schema.
- Add database migrations before changing the SQLite table shape.
- Consider wrapping SQLite and TOML errors in `AgeCalcError` for cleaner CLI behavior.
- Add direct tests for CLI commands with an `InMemoryProfileRepository`.
- Preserve the runtime dependency-free design unless a clear requirement justifies adding a package.

---

# Lessons Learned

## App 29 — Age Calculator

**Standalone CLI Utility Group | Document 5 of 5**

## Project Summary

Age Calculator started as a familiar beginner project idea: calculate someone’s age from a birthdate. The final implementation turns that simple idea into a small layered CLI application. It calculates calendar age accurately enough for user-facing output, detects ambiguous date inputs, supports milestones, saves named profiles, and provides both plain text and JSON output.

The most important architectural choice was to avoid treating the CLI as the application. The CLI is only an adapter. The real system is made of reusable domain objects, pure calculation functions, parser strategies, application services, formatter strategies, and repositories.

This makes the project more valuable than a typical age calculator. It shows how even a small utility can be designed with boundaries.

## Original Goals vs. Actual Outcome

### Original goals

- Build a Python CLI age calculator.
- Accept birthdate input.
- Calculate years, months, and days.
- Practice date handling.
- Keep the project understandable.

### Actual outcome

- Built a packaged CLI with an `agecalc` console script.
- Added layered architecture.
- Added immutable `Age` and `Profile` domain models.
- Added parser strategies for ISO, US, and EU dates.
- Added ambiguity detection.
- Added `singledispatch` input normalization.
- Added milestone generation.
- Added saved profiles with SQLite persistence.
- Added plain and JSON formatter strategies.
- Added config loading from TOML.
- Added type-checking and linting setup.

The final outcome exceeds the original “calculator” scope, but still remains small enough to be reviewed as a focused CLI project.

## Technical Decisions That Paid Off

### Immutable domain objects

Making `Age` and `Profile` frozen dataclasses made the domain easier to reason about. Once an age or profile is created, other layers cannot accidentally mutate it.

### Separate calculation layer

Keeping `age_at` pure paid off immediately. It can be called by the CLI, services, profiles, tests, or external library users without needing config, database, or terminal state.

### Explicit parser strategies

Date parsing is one of the easiest places for a user-facing calculator to lie. The parser registry makes supported formats explicit and catches ambiguity instead of silently choosing one interpretation.

### `singledispatch` factory

The `create_age` factory demonstrates a Python-specific pattern well. It allows strings, dates, datetimes, and tuples to be supported without a long chain of `if` statements in service code.

### Repository abstraction

The profile repository interface creates a clean seam between use cases and storage. SQLite is useful for real CLI use, while the in-memory repository keeps testing simple.

### Formatter strategies

Plain text and JSON output have different audiences. Keeping output formatters separate prevents JSON serialization details from leaking into age calculations or profile logic.

### Command objects

Each CLI command maps to a class with an `execute()` method. This is more organized than putting all command behavior in one giant `main()` function.

## Technical Decisions That Created Debt

### SQLite without migrations

The database schema is created automatically, but there is no schema version or migration path. This is fine for the first version, but future profile fields would require careful handling.

### Partial exception wrapping

Application-level errors are cleanly caught as `AgeCalcError`, but lower-level TOML, filesystem, SQLite, or unexpected runtime errors may surface less cleanly.

### Config without validation schema

The config loader reads values and supplies defaults, but it does not strictly validate accepted values. Bad `output_format` is caught by argparse choices, but other invalid config values may behave indirectly.

### Date parser ambiguity policy is strict

Rejecting ambiguity is correct, but some users may find it surprising. The app should explain this clearly in help text and docs.

### More architecture than the domain strictly needs

For a tiny utility, command objects, repositories, protocols, strategies, and services may feel heavy. The trade-off is justified for learning, but it should not become a habit to over-architect every script.

## What Was Harder Than Expected

### Calendar age is not simple subtraction

Calculating age in years, months, and days requires respecting month lengths, anniversaries, and leap-year birthdays. Dividing by 365 would not be acceptable for user-facing age output.

### Leap-day behavior requires a policy

February 29 birthdays force a product decision. The app chooses February 28 in non-leap years. That is reasonable, but it is still a policy, not a universal truth.

### Ambiguous slash dates are dangerous

Supporting both US and EU date formats makes inputs like `03/04/2000` risky. Detecting ambiguity is harder than just trying formats until one succeeds, but it produces safer behavior.

### CLI option placement can be subtle

Supporting `--format` globally and after subcommands requires deliberate parser setup. This is a real CLI usability detail.

### Keeping layers thin takes discipline

It is easy for services to become bloated or for CLI command classes to start doing domain work. The design requires regularly asking, “Which layer owns this?”

## What Was Easier Than Expected

### SQLite is enough for local profile storage

The built-in `sqlite3` module provides a lot of value with minimal setup. For a local CLI tool, it is a good step up from JSON files.

### `argparse` can support a real command tree

Even without Typer or Click, `argparse` supports nested commands, choices, validation hooks, and subcommand dispatch.

### Dataclasses improve readability

The domain models and milestone records are easier to understand as dataclasses than as loose dictionaries.

### Protocols fit strategy interfaces well

The parser and formatter boundaries are simple enough that protocols are readable and useful.

### JSON output was easy once formatter boundaries existed

Because output formatting is isolated, adding JSON did not require changing calculations, services, or repositories.

## Python-Specific Learnings

### `dataclass(frozen=True)`

Frozen dataclasses are a strong fit for value objects. They reduce accidental mutation and make domain models feel more trustworthy.

### `functools.total_ordering`

`Age` only needs to define equality and less-than to gain the rest of the comparison methods.

### `functools.singledispatch`

`singledispatch` is useful when behavior varies by input type. It kept age creation open to extension while keeping each case focused.

### `ContextVar`

`ContextVar` is more controlled than a plain module global for temporary reference-date overrides.

### `lru_cache`

Caching weekday calculation is not necessary for tiny inputs, but it demonstrates a safe optimization around a pure function.

### `heapq`

A heap is a clean way to merge multiple sorted infinite milestone streams without generating everything upfront.

### `tomllib`

Python 3.11’s built-in TOML reader makes config loading possible without runtime dependencies.

### `sqlite3`

The standard library database module is enough for small persistent CLI tools.

### `pathlib`

`Path.home()`, `expanduser()`, and parent directory creation make config/database path handling clearer than string paths.

## Architecture Insights

### Small apps still benefit from boundaries

The app’s value comes from clean separation more than feature count. Each module has a reason to exist.

### The CLI should be an adapter

A strong CLI does not mean the CLI should own the business logic. The command classes translate user intent into service calls.

### Repositories make persistence replaceable

The profile system would be harder to test if services depended directly on SQLite. The repository interface solves that.

### Strict parsing is a user-safety feature

It is better for a CLI to reject ambiguous input than to return a precise-looking wrong answer.

### Output format is a contract

Plain text is for humans. JSON is for scripts. Keeping both behind a formatter interface makes this distinction explicit.

### Domain exceptions improve CLI experience

A project-specific exception hierarchy lets the CLI handle expected errors cleanly.

## Testing Gaps

The repository declares pytest, Hypothesis, Ruff, and mypy checks, and the source code is structured to be testable. Individual test files were not available through direct repository file fetch during this documentation pass, so the following are recommended or expected coverage areas rather than confirmed file-by-file claims.

### High-priority tests

- `age_at` for normal birthdays.
- `age_at` for February 29 birthdays.
- Future birthdate rejection.
- Ambiguous date detection.
- Invalid date rejection.
- `create_age` dispatch for strings, dates, datetimes, tuples, and unsupported types.
- Milestone ordering and limit handling.
- `Age` equality, ordering, subtraction, and formatting.
- `Profile.create` empty-name validation.
- `InMemoryProfileRepository` save/get/list/delete.
- `SQLiteProfileRepository` persistence and case-insensitive lookup.
- CLI success path for each command.
- CLI error path for invalid dates and missing profiles.
- JSON output validity.
- Config fallback behavior when config file is absent.
- Timezone fallback behavior when zone lookup fails.

### Property-based test opportunities

- Age total seconds should never be negative for valid birthdate/reference pairs.
- Generated milestone dates should be strictly non-decreasing.
- Parser registry should reject dates with multiple conflicting interpretations.
- Saving and loading a profile through SQLite should preserve name and birthdate.

## Reusable Patterns Identified

### Parser registry

The `ParserRegistry` pattern can be reused in any CLI where multiple input syntaxes are supported but ambiguity must be detected.

### Service + repository

`ProfileService` plus `ProfileRepository` is reusable for apps with small local data stores.

### Formatter strategy

The plain/JSON formatter split can be reused across portfolio CLI apps that need both human and machine-readable output.

### Command object dispatch

The `COMMANDS` dictionary and command class pattern scales well for multi-command CLIs.

### Context-managed clock override

`reference_date()` is a reusable approach for deterministic date/time tests.

### Immutable result objects

`Age` and `Milestone` show how results can be structured and passed between layers without dictionaries everywhere.

## If I Built This Again

### Add database migrations early

Even a tiny SQLite app benefits from a `schema_version` table before the first schema change.

### Wrap storage/config errors

I would convert common SQLite, TOML, and filesystem errors into `AgeCalcError` subclasses so the CLI always fails cleanly.

### Add a `--config` option

The current config path is fixed at `~/.agecalc/config.toml`. A `--config` flag would make testing and demos easier.

### Add a `--database` option

A direct database override would help users keep separate profile sets without editing config.

### Improve help text around ambiguous dates

The CLI should explicitly recommend ISO dates when ambiguity occurs.

### Add richer profile metadata only after migrations

Fields like notes, timezone, or tags are tempting, but they should wait until persistence versioning exists.

### Add a test fixture CLI repository

`main(argv, repository=None)` already supports injecting a repository. I would build CLI tests around `InMemoryProfileRepository` so profile commands can be tested without SQLite files.

### Consider shell completion only after CLI stabilizes

Argparse is enough now. Shell completion or Typer would be premature unless command count grows.

## Open Questions

- Should leap-day birthdays be treated as February 28 or March 1 in non-leap years?
- Should ambiguous dates be rejected always, or should `preferred_date_format` break ties?
- Should JSON output include a schema version?
- Should profile names be unique case-insensitively in SQLite at the database constraint level?
- Should the app expose a `--config` or `--database` override?
- Should timezone be applied only to default reference date, or also stored per profile?
- Should the app add import/export for profile data?
- Should storage/config exceptions become first-class `AgeCalcError` subclasses?
- Should future versions support time-of-day precision?
- Should the package keep runtime dependencies at zero if CLI complexity increases?

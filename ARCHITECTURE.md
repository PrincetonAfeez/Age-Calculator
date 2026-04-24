# Architecture

This project is organized as a small layered CLI application. The goal is not to make a huge framework, but to keep each responsibility obvious and testable.

```text
User
  |
  v
CLI and Commands
  |
  v
Application Services
  |
  +--> Domain calculations and parsing
  |
  +--> ProfileRepository interface
          |
          +--> SQLiteProfileRepository
          |
          +--> InMemoryProfileRepository
```

## Layers

The CLI layer lives in `agecalc.cli`. It owns `argparse`, subcommands, and selecting an output formatter. Each subcommand maps to a command class with an `execute(args)` method, so adding a new command does not require one large conditional block.

The service layer lives in `agecalc.services`. Services represent application use cases such as calculating an age, finding milestones, or managing saved profiles. The profile service receives a `ProfileRepository` through its constructor. That is the dependency injection point: production uses SQLite, tests use memory.

The domain layer lives in `agecalc.domain`, `agecalc.calculations`, `agecalc.parsing`, and `agecalc.factory`. It contains the immutable `Age` and `Profile` dataclasses, pure age calculations, custom exceptions, parser strategies, and the `singledispatch` age factory.

The storage layer lives in `agecalc.storage`. `ProfileRepository` is the abstract interface. `SQLiteProfileRepository` persists profiles to disk, while `InMemoryProfileRepository` is fast and deterministic for tests.

## Why This Shape

The main design choice is separation of concerns. Date parsing is not mixed into the CLI. SQLite does not appear inside age calculations. Formatters do not know how repositories work. This keeps each module small enough to understand and makes the tests focused.

The parser registry is an example of the strategy pattern. Each parser knows one format, and the registry coordinates them. Ambiguous dates are rejected because silently guessing a birthdate would be worse than asking the user to provide a clearer ISO date.

The repository pattern keeps storage replaceable. The CLI composes the real SQLite repository at the application boundary, while tests inject `InMemoryProfileRepository`. That makes the dependency direction clear: services depend on an interface, not a concrete database.

The clock override context manager exists because date-based programs are otherwise hard to test. Code can use `reference_date(date(...))` to make "today" deterministic without monkeypatching global functions.

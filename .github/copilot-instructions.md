# Project Guidelines

## Code Style
- Keep changes typed and explicit, following existing patterns in [src/snake3d/core/engine.py](src/snake3d/core/engine.py) and [src/snake3d/core/rules.py](src/snake3d/core/rules.py).
- Prefer small, pure helpers in core logic and keep side effects in adapters.
- Preserve the existing test style that uses lightweight fake adapters instead of heavy mocking, as shown in [tests/test_engine.py](tests/test_engine.py).

## Architecture
- This repository follows a ports-and-adapters layout under [src/snake3d](src/snake3d):
- Core domain and game rules are in [src/snake3d/core](src/snake3d/core).
- Port protocols are in [src/snake3d/ports](src/snake3d/ports).
- Concrete terminal implementations are in [src/snake3d/adapters](src/snake3d/adapters).
- Keep core modules independent of terminal and input implementation details.

## Build And Test
- Install dependencies with Poetry: `poetry install`
- Run tests with Poetry: `poetry run pytest`
- Run the game entrypoint: `poetry run snake3d`

## Conventions
- Use Poetry for project workflows in this repository.
- Keep [poetry.lock](poetry.lock) in version control when dependencies change.
- Target runtime is Python 3.14 per [pyproject.toml](pyproject.toml).
- Terminal rendering depends on ANSI behavior and Windows console setup in [src/snake3d/adapters/terminal_renderer.py](src/snake3d/adapters/terminal_renderer.py).
- If touching startup flow, note that input provider wiring is currently not implemented in [src/snake3d/__main__.py](src/snake3d/__main__.py).

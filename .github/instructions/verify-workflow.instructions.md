---
description: "Enforce running Ruff and Mypy before running tests when verifying changes."
name: "Verify Workflow: Ruff + Mypy before Pytest"
applyTo: "*"
---

# Purpose

- Ensure quick, deterministic feedback by running linting and static typing checks before executing the test suite.

# Rule

- When verifying changes locally or in CI (PRs), run `ruff` and `mypy` before `pytest`.

# Reasoning

- `ruff` is fast and catches style, import and common errors early.
- `mypy` catches type-level issues that tests may not cover and prevents a class of runtime bugs.
- Running these before `pytest` reduces noisy test failures and speeds developer feedback loops.

# Recommended commands

- Lint and format checks:

  - `poetry run ruff check .`
  - `poetry run ruff format --check .`

- Type checks:

  - `poetry run mypy src tests`

- Tests:

  - `poetry run pytest`

# Example GitHub Actions job (minimal)

```yaml
name: verify
on: [pull_request]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.14'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install poetry
          poetry install --only dev
      - name: Ruff (lint/format)
        run: |
          poetry run ruff check .
          poetry run ruff format --check .
      - name: Mypy (type check)
        run: poetry run mypy src tests
      - name: Tests
        run: poetry run pytest
```

# Notes & examples

- For local pre-commit hooks consider adding `ruff` and `mypy` to your `pre-commit` config so checks run before commits/PRs.
- This instruction applies repository-wide (`applyTo: "*"`). If you want narrower scope, update `applyTo` accordingly.

If you want, I can: add a CI job file, a `pre-commit` config snippet, or enforce this in README/CONTRIBUTING.

---
description: "Use when writing or updating pytest tests, engine tests, rules tests, or terminal renderer tests in Snake3D. Covers fake adapters, deterministic randomness, and assertion style."
name: "Snake3D Test Style"
applyTo: "tests/**/*.py"
---
# Snake3D Test Style

- Prefer lightweight fake adapters over heavy mocking, following [tests/test_engine.py](tests/test_engine.py).
- Keep tests deterministic by using fixed seeds for random.Random where randomness is involved.
- Match existing pytest style: clear arrange-act-assert flow with direct assertions on behavior.
- For engine tests, verify lifecycle behavior through adapter state (for example, rendered frames, initialize and shutdown calls).
- Keep test names explicit about expected behavior.
- When adding behavior in core modules, add or update focused tests in [tests/test_engine.py](tests/test_engine.py), [tests/test_rules.py](tests/test_rules.py), or [tests/test_terminal_renderer.py](tests/test_terminal_renderer.py) as appropriate.
- Validate changes with Poetry: `poetry run pytest`.
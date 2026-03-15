---
description: "Use when editing Snake3D core logic, architecture boundaries, ports-and-adapters wiring, engine code, rules code, or state management. Covers keeping core modules independent from terminal and input implementation details."
name: "Snake3D Core Boundaries"
applyTo: "src/snake3d/core/**/*.py"
---
# Snake3D Core Boundaries

- Keep core modules in [src/snake3d/core](src/snake3d/core) independent from terminal rendering, console behavior, and concrete input handling.
- Do not import from [src/snake3d/adapters](src/snake3d/adapters) inside core modules.
- Express external dependencies through protocols in [src/snake3d/ports](src/snake3d/ports) and wire concrete implementations at the application edge.
- Prefer small, pure helpers in core logic and keep side effects in adapters or startup wiring.
- Follow the typed, explicit style in [src/snake3d/core/engine.py](src/snake3d/core/engine.py) and [src/snake3d/core/rules.py](src/snake3d/core/rules.py).
- If a change requires new renderer or input behavior, extend a port first, then update the adapter and entrypoint instead of pushing implementation details into core.
- When startup wiring changes are needed, keep them in [src/snake3d/__main__.py](src/snake3d/__main__.py).

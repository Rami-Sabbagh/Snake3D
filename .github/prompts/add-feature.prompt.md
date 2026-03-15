---
description: "Add or change a Snake3D feature with architecture-safe implementation, tests, and validation."
name: "Add Snake3D Feature"
argument-hint: "Describe the feature, constraints, and acceptance criteria"
agent: "agent"
---
Implement the requested Snake3D feature in this workspace.

Use the chat input as the feature request, including any constraints, target behavior, and acceptance criteria.

Requirements:
- Start by locating the relevant code paths and deciding whether the change belongs in core, ports, adapters, tests, or startup wiring.
- Follow [project guidelines](../copilot-instructions.md), [core boundaries](../instructions/core-boundaries.instructions.md), and [test style](../instructions/test-style.instructions.md).
- Ask only the minimum clarifying questions needed if the request is genuinely ambiguous. Otherwise, proceed with implementation.
- Prefer root-cause changes over surface patches.
- Keep core logic in [../../src/snake3d/core](../../src/snake3d/core) independent from concrete terminal and input implementation details.
- If new renderer or input behavior is needed, extend a port and wire the concrete implementation at the application edge.
- Add or update focused tests when behavior changes.
- Validate the result with Poetry commands that fit the change, especially `poetry run pytest` when tests are affected.

Response format:
1. Briefly summarize the design choice.
2. Implement the change.
3. Report the key files changed.
4. Report validation performed and any remaining blockers.

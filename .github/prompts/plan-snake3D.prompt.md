## Plan: Terminal 3D Snake

Build a small, modular Python 3.14 application managed with Poetry where the game rules are independent from terminal I/O. The recommended design keeps the renderer behind a narrow interface so ANSI terminal rendering can be swapped later for another frontend without changing the core engine. The authoritative board representation should be a 3D NumPy array, with a small amount of supplemental state kept for efficient movement and collision handling. The initial release explicitly targets Windows, while still keeping terminal sizing logic portable enough to query common terminal-size sources on Windows and Linux.

**Steps**
1. Phase 1 - Bootstrap project structure: initialize a Poetry project targeting Python 3.14, define the package layout under src\snake3d, add runtime dependencies needed for numeric state management and reliable ANSI behavior on Windows, and configure pytest as the unit test runner.
2. Phase 1 - Define the domain model in the core package: represent the world as a 3D NumPy array with fixed cell codes for empty space, snake head, snake body, and food; define immutable coordinate and direction types using an explicit xyz coordinate convention throughout the codebase; and define a configuration object for board dimensions, tick rate, and control mapping. Set the initial board size to 8x8x8.
3. Phase 1 - Add supplemental state alongside the 3D array: keep the snake body as an ordered deque of coordinates, track the current movement vector, maintain the current food coordinate, and store game status such as score and terminal game-over state. This avoids scanning the entire array each tick while preserving the array as the source of board occupancy.
4. Phase 2 - Implement the game state transition layer: create pure update logic that accepts the current state plus an input direction and produces the next state by moving the head, clearing or preserving the tail, resolving food consumption, spawning new food, and detecting wall or self collisions. Use a seeded random generator in tests so food placement is deterministic, and use a non-fixed random seed in normal play. This step blocks the engine and renderer work because they depend on a stable state API.
5. Phase 2 - Define the renderer abstraction: create a renderer protocol or abstract base class with narrow responsibilities such as initialize terminal session, build a full frame string from the current state snapshot, render overlays like score/game over, and restore terminal state on shutdown. Keep frame construction separate from terminal writes so renderer output can be unit tested directly, and keep the engine dependent only on this abstraction.
6. Phase 2 - Implement terminal rendering as a replaceable adapter: add a terminal renderer that converts the 3D array into a 2D textual presentation centered on the snake head. Display only the current head slice, the slice above, and the slice below, with clear 0-based level labels and consistent spacing. When the head is at the top or bottom edge, keep the three-panel layout stable by rendering missing slices as gray placeholder panels. Add a vertical bar on the right that indicates the snake head's current z-level within the full board, also using 0-based labels. Use ANSI escape sequences for cursor homing, clearing, colorization, hiding/showing cursor, and minimizing flicker by writing the entire frame buffer in a single flush.
7. Phase 2 - Implement non-blocking terminal input: isolate key handling into its own component so Windows-specific input details do not leak into the engine. Map keys to 3D movement directions, reject instant reversal moves, and provide controls for pause, restart, and quit if included in scope.
8. Phase 3 - Implement the engine loop: orchestrate initialization, non-blocking input polling, tick-based state updates, renderer calls, and frame timing. The engine should own high-level lifecycle only and delegate state mutation, rendering, and input interpretation to separate components. Accept at most one pending turn per tick so rapid input remains predictable and testable.
9. Phase 3 - Handle terminal lifecycle and sizing concerns: detect terminal dimensions using commonly available mechanisms such as environment variables and standard terminal-size APIs, enable ANSI support on Windows terminals at startup, restore cursor visibility and terminal state on exit, and guard against common issues such as flicker, partial writes, and unsupported terminals. The first release is intentionally Windows-only, but terminal-size detection should avoid hard-coding Windows-exclusive assumptions.
10. Phase 4 - Add pytest unit tests for the core logic: test state transitions, growth after food consumption, collision detection, food spawning constraints, fixed-seed food placement behavior, one-pending-turn input handling, and synchronization between the deque-based snake representation and the 3D NumPy array. These tests can run without the terminal renderer.
11. Phase 4 - Add pytest unit tests for the terminal renderer: verify the rendered output for representative states, including the correct three-slice window around the head, gray placeholder panels at the edges, 0-based labels, the right-side level bar, and ANSI-decorated frame composition.
12. Phase 4 - Add lightweight integration verification: exercise the engine with a fake renderer and fake input provider to verify tick progression, lifecycle handling, and renderer independence without relying on real terminal behavior.
13. Phase 4 - Add a simple CLI entrypoint: wire a main module that constructs config, state manager, input adapter, and terminal renderer, then starts the engine. Keep options minimal unless argument parsing is explicitly desired later.

**Relevant files**
- pyproject.toml - Poetry metadata, Python 3.14 constraint, runtime dependencies, pytest configuration, and console entry point.
- src\snake3d\__main__.py - application startup and dependency wiring.
- src\snake3d\core\models.py - coordinate types using xyz ordering, enums or constants for cell values, and configuration objects.
- src\snake3d\core\state.py - 3D NumPy board ownership and snake/food state.
- src\snake3d\core\rules.py - pure transition logic for movement, growth, collisions, and food spawning.
- src\snake3d\core\engine.py - main tick loop and lifecycle orchestration.
- src\snake3d\ports\renderer.py - renderer abstraction used by the engine.
- src\snake3d\ports\input.py - input abstraction used by the engine.
- src\snake3d\adapters\terminal_renderer.py - ANSI-based terminal rendering implementation.
- src\snake3d\adapters\terminal_input_windows.py - Windows-specific non-blocking key capture.
- src\snake3d\adapters\terminal_size.py - terminal dimension detection using environment variables and standard terminal-size APIs.
- tests\test_rules.py - core state transition tests.
- tests\test_terminal_renderer.py - pytest coverage for terminal renderer output.
- tests\test_engine.py - engine tests with fake adapters.

**Verification**
1. Run the pytest suite to validate core game rules independently of the terminal adapter.
2. Add deterministic pytest cases for movement across all three axes, for illegal reversal input, and for the engine's one-pending-turn-per-tick behavior.
3. Verify with fixed-seed tests that food spawning is deterministic in test mode and uses non-fixed seeding in normal play.
4. Verify with renderer unit tests that only the head slice, the slice above, and the slice below are displayed, that out-of-range slices become gray placeholders, and that the right-side level bar marks the current head level correctly with 0-based labels.
5. Verify that the renderer can be replaced with a fake implementation without changing engine code.
6. Run the game manually in Windows Terminal to confirm ANSI cursor movement, colors, screen refresh stability, slice-window readability, level-bar clarity, terminal-size adaptation, and cursor restoration on exit.
7. Confirm the displayed board stays synchronized with the NumPy array and the internal snake deque after repeated growth and collision scenarios.

**Decisions**
- Included: Python 3.14, Poetry-based dependency management, ANSI terminal control, 3D NumPy board storage, and renderer decoupling.
- Included: a supplemental deque for snake ordering because the NumPy array alone is inefficient for tail updates and body traversal.
- Included: a ports-and-adapters style split so the terminal frontend can be replaced later.
- Included: an explicit xyz coordinate convention across the codebase, an initial 8x8x8 board, and 0-based level labels in the UI.
- Included: deterministic food spawning in tests via a fixed seed, and non-fixed random seeding for normal play.
- Included: a stable three-panel renderer layout with gray placeholders when adjacent slices are out of range.
- Included: one pending turn per tick in the engine so input handling remains predictable.
- Included: Windows-only support for the first release.
- Excluded for initial scope: sound, persistent scores, AI/autoplay, multiplayer, and advanced CLI configuration.
- Recommended display model: render a focused three-slice window consisting of the snake head's current z-level plus the slices immediately above and below it, because it keeps gameplay legible in a terminal and matches the underlying data shape without overwhelming the screen.

**Further Considerations**
1. Control scheme recommendation: use W/A/S/D for planar movement and R/F for vertical movement; this is simple and avoids arrow-key parsing complexity in the first version.
2. Terminal setup recommendation: prefer direct ANSI plus minimal Windows setup support, with a small compatibility helper only if needed for older consoles.
3. Terminal sizing recommendation: use environment variables when present and fall back to standard terminal-size APIs so layout decisions are not tied to a single shell implementation.
4. Renderer testing recommendation: keep frame construction deterministic so pytest can compare the visible output structure, including labels, placeholder panels, slices, and the level bar, without depending on a live terminal.
5. Board-size recommendation: target an initial 8x8x8 grid and adjust the rendered layout based on detected terminal size so the three-slice renderer and level bar stay readable.

**Sample Preview**
```text
Snake3D  score=07  dir=(+1,0,0)  head=(3,4,5)  grid=8x8x8

z=4            z=5            z=6                            levels
. . . . . . . .  . . . . . . . .  . . . . . . . .           0 | |
. . . . . . . .  . . . . . . . .  . . . . . . . .           1 | |
. . . . . . . .  . . . o o . . .  . . . . . . . .           2 | |
. . . . . . . .  . . . . O . . .  . . . . . . . .           3 |#|
. . . . . . . .  . . . . . . . .  . . . . . . . .           4 | |
. . . . . . . .  . . . . * . . .  . . . . . . . .           5 | |
. . . . . . . .  . . . . . . . .  . . . . . . . .           6 | |
. . . . . . . .  . . . . . . . .  . . . . . . . .           7 | |

Legend: O=head  o=body  *=food  .=empty  gray panel=out-of-range slice
```

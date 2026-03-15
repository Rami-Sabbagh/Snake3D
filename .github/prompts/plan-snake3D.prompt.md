## Plan: Terminal 3D Snake

Build a small, modular Python 3.14 application managed with Poetry where the game rules are independent from terminal I/O. The recommended design keeps the renderer behind a narrow interface so ANSI terminal rendering can be swapped later for another frontend without changing the core engine. The authoritative board representation should be a 3D NumPy array, with a small amount of supplemental state kept for efficient movement and collision handling.

**Steps**
1. Phase 1 - Bootstrap project structure: initialize a Poetry project targeting Python 3.14, define the package layout under c:\Users\Rami\Documents\Snake3D\src\snake3d, and add runtime dependencies needed for numeric state management and reliable ANSI behavior on Windows.
2. Phase 1 - Define the domain model in the core package: represent the world as a 3D NumPy array with fixed cell codes for empty space, snake head, snake body, and food; define immutable coordinate and direction types; define a configuration object for board dimensions, tick rate, and control mapping.
3. Phase 1 - Add supplemental state alongside the 3D array: keep the snake body as an ordered deque of coordinates, track the current movement vector, maintain the current food coordinate, and store game status such as score and terminal game-over state. This avoids scanning the entire array each tick while preserving the array as the source of board occupancy.
4. Phase 2 - Implement the game state transition layer: create pure update logic that accepts the current state plus an input direction and produces the next state by moving the head, clearing or preserving the tail, resolving food consumption, spawning new food, and detecting wall or self collisions. This step blocks the engine and renderer work because they depend on a stable state API.
5. Phase 2 - Define the renderer abstraction: create a renderer protocol or abstract base class with narrow responsibilities such as initialize terminal session, render one frame from the current state snapshot, render overlays like score/game over, and restore terminal state on shutdown. Keep the engine dependent only on this abstraction.
6. Phase 2 - Implement terminal rendering as a replaceable adapter: add a terminal renderer that converts the 3D array into a 2D textual presentation, most likely as stacked slices per z-level with clear labels and consistent spacing. Use ANSI escape sequences for cursor homing, clearing, colorization, hiding/showing cursor, and minimizing flicker by writing the entire frame buffer in a single flush.
7. Phase 2 - Implement non-blocking terminal input: isolate key handling into its own component so Windows-specific input details do not leak into the engine. Map keys to 3D movement directions, reject instant reversal moves, and provide controls for pause, restart, and quit if included in scope.
8. Phase 3 - Implement the engine loop: orchestrate initialization, non-blocking input polling, tick-based state updates, renderer calls, and frame timing. The engine should own high-level lifecycle only and delegate state mutation, rendering, and input interpretation to separate components.
9. Phase 3 - Handle terminal lifecycle and portability concerns: enable ANSI support on Windows terminals at startup, restore cursor visibility and terminal state on exit, and guard against common issues such as flicker, partial writes, and unsupported terminals. If a helper like colorama is used, keep it confined to terminal setup rather than core logic.
10. Phase 4 - Add tests for the core logic: unit test state transitions, growth after food consumption, collision detection, food spawning constraints, and synchronization between the deque-based snake representation and the 3D NumPy array. These tests can run without the terminal renderer.
11. Phase 4 - Add lightweight integration verification: exercise the engine with a fake renderer and fake input provider to verify tick progression, lifecycle handling, and renderer independence without relying on real terminal behavior.
12. Phase 4 - Add a simple CLI entrypoint: wire a main module that constructs config, state manager, input adapter, and terminal renderer, then starts the engine. Keep options minimal unless argument parsing is explicitly desired later.

**Relevant files**
- c:\Users\Rami\Documents\Snake3D\pyproject.toml - Poetry metadata, Python 3.12 constraint, dependencies, and console entry point.
- c:\Users\Rami\Documents\Snake3D\src\snake3d\__main__.py - application startup and dependency wiring.
- c:\Users\Rami\Documents\Snake3D\src\snake3d\core\models.py - coordinate types, enums or constants for cell values, and configuration objects.
- c:\Users\Rami\Documents\Snake3D\src\snake3d\core\state.py - 3D NumPy board ownership and snake/food state.
- c:\Users\Rami\Documents\Snake3D\src\snake3d\core\rules.py - pure transition logic for movement, growth, collisions, and food spawning.
- c:\Users\Rami\Documents\Snake3D\src\snake3d\core\engine.py - main tick loop and lifecycle orchestration.
- c:\Users\Rami\Documents\Snake3D\src\snake3d\ports\renderer.py - renderer abstraction used by the engine.
- c:\Users\Rami\Documents\Snake3D\src\snake3d\ports\input.py - input abstraction used by the engine.
- c:\Users\Rami\Documents\Snake3D\src\snake3d\adapters\terminal_renderer.py - ANSI-based terminal rendering implementation.
- c:\Users\Rami\Documents\Snake3D\src\snake3d\adapters\terminal_input_windows.py - Windows-specific non-blocking key capture.
- c:\Users\Rami\Documents\Snake3D\tests\test_rules.py - core state transition tests.
- c:\Users\Rami\Documents\Snake3D\tests\test_engine.py - engine tests with fake adapters.

**Verification**
1. Run the test suite to validate core game rules independently of the terminal adapter.
2. Add deterministic tests for movement across all three axes and for illegal reversal input.
3. Verify that the renderer can be replaced with a fake implementation without changing engine code.
4. Run the game manually in Windows Terminal to confirm ANSI cursor movement, colors, screen refresh stability, and cursor restoration on exit.
5. Confirm the displayed board stays synchronized with the NumPy array and the internal snake deque after repeated growth and collision scenarios.

**Decisions**
- Included: Python 3.14, Poetry-based dependency management, ANSI terminal control, 3D NumPy board storage, and renderer decoupling.
- Included: a supplemental deque for snake ordering because the NumPy array alone is inefficient for tail updates and body traversal.
- Included: a ports-and-adapters style split so the terminal frontend can be replaced later.
- Excluded for initial scope: sound, persistent scores, AI/autoplay, multiplayer, and advanced CLI configuration.
- Recommended display model: render the 3D board as a stack of 2D slices instead of attempting perspective projection, because it keeps gameplay legible in a terminal and matches the underlying data shape.

**Further Considerations**
1. Control scheme recommendation: use W/A/S/D for planar movement and R/F for vertical movement; this is simple and avoids arrow-key parsing complexity in the first version.
2. Terminal setup recommendation: prefer direct ANSI plus minimal Windows setup support, with a small compatibility helper only if needed for older consoles.
3. Board-size recommendation: start with a compact grid such as 4x6x6 or 5x7x7 so the stacked-slice renderer stays readable within a standard terminal window.

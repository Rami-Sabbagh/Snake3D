from __future__ import annotations

import random
from typing import Final

from snake3d.adapters.terminal_input_windows import WindowsTerminalInput
from snake3d.adapters.terminal_renderer import TerminalRenderer
from snake3d.core.engine import Engine
from snake3d.core.models import GameConfig
from snake3d.core.state import create_initial_state

DEFAULT_GRID: Final[tuple[int, int, int]] = (8, 8, 8)
DEFAULT_TICK_RATE_HZ: Final[float] = 6.0


def _prompt_tick_rate() -> float:
    raw_value = input(f"Tick speed (ticks/sec) [{DEFAULT_TICK_RATE_HZ}]: ").strip()
    if not raw_value:
        return DEFAULT_TICK_RATE_HZ
    try:
        value = float(raw_value)
    except ValueError:
        print(f"Invalid tick speed. Using default {DEFAULT_TICK_RATE_HZ}.")
        return DEFAULT_TICK_RATE_HZ

    if value <= 0:
        print(f"Tick speed must be positive. Using default {DEFAULT_TICK_RATE_HZ}.")
        return DEFAULT_TICK_RATE_HZ
    return value


def _prompt_grid_size() -> tuple[int, int, int]:
    default_text = "x".join(str(size) for size in DEFAULT_GRID)
    raw_value = input(f"Grid size WxHxD [{default_text}]: ").strip().lower()
    if not raw_value:
        return DEFAULT_GRID

    normalized = raw_value.replace(",", "x").replace(" ", "")
    parts = normalized.split("x")
    if len(parts) != 3 or any(not part.isdigit() for part in parts):
        print(f"Invalid grid size. Using default {default_text}.")
        return DEFAULT_GRID

    width, height, depth = (int(parts[0]), int(parts[1]), int(parts[2]))
    if min(width, height, depth) < 4:
        print(f"Each grid dimension must be at least 4. Using default {default_text}.")
        return DEFAULT_GRID
    return (width, height, depth)


def main() -> int:
    width, height, depth = _prompt_grid_size()
    tick_rate_hz = _prompt_tick_rate()
    config = GameConfig(
        width=width,
        height=height,
        depth=depth,
        tick_rate_hz=tick_rate_hz,
    )
    rng = random.Random()
    initial_state = create_initial_state(config, rng)
    renderer = TerminalRenderer(config)
    input_provider = WindowsTerminalInput(config.controls)
    engine = Engine(
        config=config,
        state=initial_state,
        renderer=renderer,
        input_provider=input_provider,
        rng=rng,
        restart_factory=lambda: create_initial_state(config, random.Random()),
    )
    return engine.run()


if __name__ == "__main__":
    raise SystemExit(main())

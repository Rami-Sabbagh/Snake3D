from __future__ import annotations

import random

from snake3d.adapters.terminal_input_windows import WindowsTerminalInput
from snake3d.adapters.terminal_renderer import TerminalRenderer
from snake3d.core.engine import Engine
from snake3d.core.models import GameConfig
from snake3d.core.state import create_initial_state


def main() -> int:
    config = GameConfig()
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

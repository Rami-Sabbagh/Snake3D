from __future__ import annotations

import time
from random import Random
from typing import Callable

from snake3d.core.models import Direction, GameConfig
from snake3d.core.rules import step_state
from snake3d.core.state import GameState
from snake3d.ports.input import InputAction, InputActionType, InputProvider
from snake3d.ports.renderer import Renderer


class Engine:
    def __init__(
        self,
        *,
        config: GameConfig,
        state: GameState,
        renderer: Renderer,
        input_provider: InputProvider,
        rng: Random,
        restart_factory: Callable[[], GameState],
        clock: Callable[[], float] = time.monotonic,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> None:
        self.config = config
        self.state = state
        self.renderer = renderer
        self.input_provider = input_provider
        self.rng = rng
        self.restart_factory = restart_factory
        self.clock = clock
        self.sleep_fn = sleep_fn
        self.pending_direction: Direction | None = None
        self.pending_vertical_direction: Direction | None = None
        self.is_paused = False
        self.quit_requested = False

    def handle_action(self, action: InputAction | None) -> None:
        if action is None:
            return

        if action.kind is InputActionType.QUIT:
            self.quit_requested = True
            return

        if action.kind is InputActionType.PAUSE:
            self.is_paused = not self.is_paused
            return

        if action.kind is InputActionType.RESTART:
            self.state = self.restart_factory()
            self.pending_direction = None
            self.pending_vertical_direction = None
            self.is_paused = False
            return

        if (
            action.kind is InputActionType.VERTICAL
            and action.direction is not None
            and self.pending_vertical_direction is None
        ):
            self.pending_vertical_direction = action.direction
            return

        if (
            action.kind is InputActionType.DIRECTION
            and action.direction is not None
            and self.pending_direction is None
        ):
            if not action.direction.is_opposite(self.state.direction):
                self.pending_direction = action.direction

    def tick(self) -> GameState:
        if not self.is_paused and not self.state.is_game_over:
            if self.pending_vertical_direction is not None:
                previous_direction = self.state.direction
                self.state = step_state(
                    self.state,
                    self.config,
                    self.pending_vertical_direction,
                    self.rng,
                )
                self.state.direction = previous_direction
            else:
                self.state = step_state(
                    self.state, self.config, self.pending_direction, self.rng
                )
        self.pending_direction = None
        self.pending_vertical_direction = None
        self.renderer.render(self.state)
        return self.state

    def run(self, *, max_ticks: int | None = None) -> int:
        tick_interval = 1.0 / self.config.tick_rate_hz
        ticks = 0
        self.renderer.initialize()
        self.renderer.render(self.state)
        next_tick = self.clock() + tick_interval

        try:
            while not self.quit_requested:
                self.handle_action(self.input_provider.poll_action())
                if self.quit_requested:
                    break

                now = self.clock()
                if now >= next_tick:
                    self.tick()
                    ticks += 1
                    next_tick += tick_interval
                    if max_ticks is not None and ticks >= max_ticks:
                        break
                    continue

                self.sleep_fn(min(next_tick - now, 0.01))
        finally:
            self.renderer.shutdown()

        return 0

from __future__ import annotations

import random
from collections import deque

from snake3d.core.engine import Engine
from snake3d.core.models import ASCEND, DOWN, RIGHT, UP, Coord, GameConfig
from snake3d.core.state import GameState, create_state
from snake3d.ports.input import InputAction, InputActionType


class FakeRenderer:
    def __init__(self) -> None:
        self.initialized = 0
        self.shutdowns = 0
        self.frames: list[tuple[int, int, int]] = []

    def initialize(self) -> None:
        self.initialized += 1

    def build_frame(self, state: GameState) -> str:
        return str(state.head.as_tuple())

    def render(self, state: GameState) -> None:
        self.frames.append(state.head.as_tuple())

    def shutdown(self) -> None:
        self.shutdowns += 1


class FakeInputProvider:
    def __init__(self, actions: list[InputAction | None]) -> None:
        self.actions = deque(actions)

    def poll_action(self) -> InputAction | None:
        if self.actions:
            return self.actions.popleft()
        return None


class FakeClock:
    def __init__(self) -> None:
        self.value = 0.0

    def __call__(self) -> float:
        return self.value

    def sleep(self, seconds: float) -> None:
        self.value += seconds


def test_engine_accepts_only_one_pending_turn_per_tick() -> None:
    config = GameConfig(width=8, height=8, depth=8, tick_rate_hz=5.0)
    state = create_state(
        config,
        [Coord(3, 3, 3), Coord(2, 3, 3), Coord(1, 3, 3)],
        RIGHT,
        food=Coord(7, 7, 7),
    )
    clock = FakeClock()
    renderer = FakeRenderer()
    input_provider = FakeInputProvider(
        [
            InputAction(InputActionType.DIRECTION, UP),
            InputAction(InputActionType.DIRECTION, DOWN),
        ]
    )
    engine = Engine(
        config=config,
        state=state,
        renderer=renderer,
        input_provider=input_provider,
        rng=random.Random(5),
        restart_factory=lambda: state,
        clock=clock,
        sleep_fn=clock.sleep,
    )

    engine.run(max_ticks=1)

    assert renderer.frames[-1] == (3, 2, 3)


def test_engine_handles_lifecycle_with_fake_adapters() -> None:
    config = GameConfig(width=8, height=8, depth=8, tick_rate_hz=4.0)
    state = create_state(
        config,
        [Coord(3, 3, 3), Coord(2, 3, 3), Coord(1, 3, 3)],
        RIGHT,
        food=Coord(6, 6, 6),
    )
    clock = FakeClock()
    renderer = FakeRenderer()
    input_provider = FakeInputProvider([None, None, None, None])
    engine = Engine(
        config=config,
        state=state,
        renderer=renderer,
        input_provider=input_provider,
        rng=random.Random(9),
        restart_factory=lambda: state,
        clock=clock,
        sleep_fn=clock.sleep,
    )

    engine.run(max_ticks=2)

    assert renderer.initialized == 1
    assert renderer.shutdowns == 1
    assert renderer.frames[0] == (3, 3, 3)
    assert len(renderer.frames) >= 2


def test_engine_vertical_move_is_one_shot_and_keeps_horizontal_direction() -> None:
    config = GameConfig(width=8, height=8, depth=8, tick_rate_hz=5.0)
    state = create_state(
        config,
        [Coord(3, 3, 3), Coord(2, 3, 3), Coord(1, 3, 3)],
        RIGHT,
        food=Coord(7, 7, 7),
    )
    clock = FakeClock()
    renderer = FakeRenderer()
    input_provider = FakeInputProvider([InputAction(InputActionType.VERTICAL, ASCEND)])
    engine = Engine(
        config=config,
        state=state,
        renderer=renderer,
        input_provider=input_provider,
        rng=random.Random(5),
        restart_factory=lambda: state,
        clock=clock,
        sleep_fn=clock.sleep,
    )

    engine.run(max_ticks=1)

    assert renderer.frames[-1] == (3, 3, 4)
    assert engine.state.direction == RIGHT

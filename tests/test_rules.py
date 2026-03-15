from __future__ import annotations

import random

import pytest

from snake3d.core.models import ASCEND, DOWN, LEFT, RIGHT, UP, Coord, GameConfig
from snake3d.core.rules import next_direction, step_state
from snake3d.core.state import create_state, is_state_synchronized, spawn_food


def test_next_direction_rejects_instant_reversal() -> None:
    assert next_direction(RIGHT, LEFT) == RIGHT


@pytest.mark.parametrize(
    ("direction", "expected_head"),
    [
        (RIGHT, Coord(3, 2, 2)),
        (DOWN, Coord(2, 3, 2)),
        (ASCEND, Coord(2, 2, 3)),
    ],
)
def test_step_state_moves_across_all_axes(direction, expected_head) -> None:
    config = GameConfig(width=8, height=8, depth=8)
    state = create_state(
        config,
        [Coord(2, 2, 2), Coord(1, 2, 2), Coord(0, 2, 2)],
        RIGHT,
        food=Coord(7, 7, 7),
    )

    next_state = step_state(state, config, direction, random.Random(4))

    assert next_state.head == expected_head
    assert len(next_state.snake) == 3
    assert is_state_synchronized(next_state, config)


def test_step_state_grows_and_respawns_food_deterministically() -> None:
    config = GameConfig(width=4, height=4, depth=4)
    state = create_state(
        config,
        [Coord(1, 1, 1), Coord(0, 1, 1), Coord(0, 0, 1)],
        RIGHT,
        food=Coord(2, 1, 1),
    )

    next_state = step_state(state, config, RIGHT, random.Random(7))
    repeated_state = step_state(state, config, RIGHT, random.Random(7))

    assert next_state.head == Coord(2, 1, 1)
    assert len(next_state.snake) == 4
    assert next_state.score == 1
    assert next_state.food == repeated_state.food
    assert next_state.food not in next_state.snake
    assert is_state_synchronized(next_state, config)


def test_step_state_detects_wall_collision() -> None:
    config = GameConfig(width=4, height=4, depth=4)
    state = create_state(
        config,
        [Coord(3, 1, 1), Coord(2, 1, 1), Coord(1, 1, 1)],
        RIGHT,
        food=Coord(0, 0, 0),
    )

    next_state = step_state(state, config, RIGHT, random.Random(1))

    assert next_state.is_game_over is True


def test_step_state_detects_self_collision() -> None:
    config = GameConfig(width=5, height=5, depth=5)
    state = create_state(
        config,
        [
            Coord(2, 2, 2),
            Coord(2, 3, 2),
            Coord(1, 3, 2),
            Coord(1, 2, 2),
            Coord(1, 1, 2),
            Coord(2, 1, 2),
        ],
        UP,
        food=Coord(4, 4, 4),
    )

    next_state = step_state(state, config, LEFT, random.Random(1))

    assert next_state.is_game_over is True


def test_spawn_food_uses_seeded_rng_and_never_uses_snake_cells() -> None:
    config = GameConfig(width=4, height=4, depth=4)
    snake = [Coord(0, 0, 0), Coord(1, 0, 0)]

    food_one = spawn_food(config, snake, random.Random(11))
    food_two = spawn_food(config, snake, random.Random(11))

    assert food_one == food_two
    assert food_one not in snake


def test_spawn_food_returns_none_when_board_is_full() -> None:
    config = GameConfig(width=4, height=4, depth=4)
    snake = [Coord(x, y, z) for z in range(4) for y in range(4) for x in range(4)]

    assert spawn_food(config, snake, random.Random(2)) is None

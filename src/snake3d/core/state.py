from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from random import Random
from typing import Deque, Iterable

import numpy as np

from snake3d.core.models import CellValue, Coord, Direction, GameConfig, RIGHT


@dataclass(slots=True)
class GameState:
    board: np.ndarray
    snake: Deque[Coord]
    direction: Direction
    foods: tuple[Coord, ...]
    score: int = 0
    is_game_over: bool = False

    @property
    def head(self) -> Coord:
        return self.snake[0]

    @property
    def food(self) -> Coord | None:
        return self.foods[0] if self.foods else None


def board_index(coord: Coord) -> tuple[int, int, int]:
    return (coord.z, coord.y, coord.x)


def spawn_food(
    config: GameConfig,
    snake: Iterable[Coord],
    rng: Random,
    occupied_extra: Iterable[Coord] = (),
) -> Coord | None:
    occupied = set(snake)
    occupied.update(occupied_extra)
    available = [
        Coord(x, y, z)
        for z in range(config.depth)
        for y in range(config.height)
        for x in range(config.width)
        if Coord(x, y, z) not in occupied
    ]
    if not available:
        return None
    return available[rng.randrange(len(available))]


def spawn_foods(
    config: GameConfig,
    snake: Iterable[Coord],
    rng: Random,
    count: int,
    existing: Iterable[Coord] = (),
) -> tuple[Coord, ...]:
    foods = list(existing)
    while len(foods) < count:
        spawned = spawn_food(config, snake, rng, occupied_extra=foods)
        if spawned is None:
            break
        foods.append(spawned)
    return tuple(foods)


def build_board(
    config: GameConfig, snake: Iterable[Coord], foods: Iterable[Coord]
) -> np.ndarray:
    board = np.full(config.board_shape, CellValue.EMPTY, dtype=np.int8)
    snake_list = list(snake)
    for segment in snake_list[1:]:
        board[board_index(segment)] = CellValue.BODY
    if snake_list:
        board[board_index(snake_list[0])] = CellValue.HEAD
    for food in foods:
        board[board_index(food)] = CellValue.FOOD
    return board


def create_state(
    config: GameConfig,
    snake: Iterable[Coord],
    direction: Direction,
    food: Coord | None = None,
    foods: Iterable[Coord] | None = None,
    *,
    score: int = 0,
    is_game_over: bool = False,
) -> GameState:
    snake_deque: Deque[Coord] = deque(snake)
    resolved_foods = tuple(foods) if foods is not None else ((food,) if food else ())
    board = build_board(config, snake_deque, resolved_foods)
    return GameState(
        board=board,
        snake=snake_deque,
        direction=direction,
        foods=resolved_foods,
        score=score,
        is_game_over=is_game_over,
    )


def create_initial_state(config: GameConfig, rng: Random) -> GameState:
    head = config.center()
    snake = deque(
        [
            head,
            Coord(head.x - 1, head.y, head.z),
            Coord(head.x - 2, head.y, head.z),
        ]
    )
    foods = spawn_foods(config, snake, rng, 3)
    return create_state(config, snake, RIGHT, foods=foods)


def is_state_synchronized(state: GameState, config: GameConfig) -> bool:
    expected = build_board(config, state.snake, state.foods)
    return np.array_equal(expected, state.board)

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
    food: Coord | None
    score: int = 0
    is_game_over: bool = False

    @property
    def head(self) -> Coord:
        return self.snake[0]


def board_index(coord: Coord) -> tuple[int, int, int]:
    return (coord.z, coord.y, coord.x)


def spawn_food(config: GameConfig, snake: Iterable[Coord], rng: Random) -> Coord | None:
    occupied = set(snake)
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


def build_board(
    config: GameConfig, snake: Iterable[Coord], food: Coord | None
) -> np.ndarray:
    board = np.full(config.board_shape, CellValue.EMPTY, dtype=np.int8)
    snake_list = list(snake)
    for segment in snake_list[1:]:
        board[board_index(segment)] = CellValue.BODY
    if snake_list:
        board[board_index(snake_list[0])] = CellValue.HEAD
    if food is not None:
        board[board_index(food)] = CellValue.FOOD
    return board


def create_state(
    config: GameConfig,
    snake: Iterable[Coord],
    direction: Direction,
    food: Coord | None,
    *,
    score: int = 0,
    is_game_over: bool = False,
) -> GameState:
    snake_deque: Deque[Coord] = deque(snake)
    board = build_board(config, snake_deque, food)
    return GameState(
        board=board,
        snake=snake_deque,
        direction=direction,
        food=food,
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
    food = spawn_food(config, snake, rng)
    return create_state(config, snake, RIGHT, food)


def is_state_synchronized(state: GameState, config: GameConfig) -> bool:
    expected = build_board(config, state.snake, state.food)
    return np.array_equal(expected, state.board)

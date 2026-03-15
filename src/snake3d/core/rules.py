from __future__ import annotations

from collections import deque
from random import Random

from snake3d.core.models import CellValue, Coord, Direction, GameConfig
from snake3d.core.state import GameState, board_index, spawn_food


def next_direction(current: Direction, requested: Direction | None) -> Direction:
    if requested is None or requested.is_opposite(current):
        return current
    return requested


def step_state(
    state: GameState,
    config: GameConfig,
    requested_direction: Direction | None,
    rng: Random,
) -> GameState:
    if state.is_game_over:
        return GameState(
            board=state.board.copy(),
            snake=deque(state.snake),
            direction=state.direction,
            food=state.food,
            score=state.score,
            is_game_over=True,
        )

    direction = next_direction(state.direction, requested_direction)
    head = state.head
    next_head = head.moved(direction)
    target = Coord(
        next_head.x % config.width,
        next_head.y % config.height,
        next_head.z % config.depth,
    )

    grow = state.food == target
    blocked_segments = list(state.snake) if grow else list(state.snake)[:-1]
    if target in blocked_segments:
        return GameState(
            board=state.board.copy(),
            snake=deque(state.snake),
            direction=direction,
            food=state.food,
            score=state.score,
            is_game_over=True,
        )

    snake = deque(state.snake)
    board = state.board.copy()

    board[board_index(head)] = CellValue.BODY
    snake.appendleft(target)
    board[board_index(target)] = CellValue.HEAD

    score = state.score
    food = state.food
    if grow:
        score += 1
        food = spawn_food(config, snake, rng)
        if food is not None:
            board[board_index(food)] = CellValue.FOOD
    else:
        tail = snake.pop()
        board[board_index(tail)] = CellValue.EMPTY

    return GameState(
        board=board,
        snake=snake,
        direction=direction,
        food=food,
        score=score,
        is_game_over=False,
    )

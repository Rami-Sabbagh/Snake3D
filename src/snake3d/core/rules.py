from collections import deque
from random import Random

from snake3d.core.models import CellValue, Coord, Direction, GameConfig
from snake3d.core.state import GameState, board_index, spawn_foods


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
            foods=state.foods,
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

    grow = target in state.foods
    blocked_segments = list(state.snake) if grow else list(state.snake)[:-1]
    if target in blocked_segments:
        return GameState(
            board=state.board.copy(),
            snake=deque(state.snake),
            direction=direction,
            foods=state.foods,
            score=state.score,
            is_game_over=True,
        )

    snake = deque(state.snake)
    board = state.board.copy()

    board[board_index(head)] = CellValue.BODY
    snake.appendleft(target)
    board[board_index(target)] = CellValue.HEAD

    score = state.score
    foods = list(state.foods)
    if grow:
        score += 1
        foods.remove(target)
    else:
        tail = snake.pop()
        board[board_index(tail)] = CellValue.EMPTY

    if grow:
        foods = list(
            spawn_foods(config, snake, rng, config.fruit_count, existing=foods)
        )

    for food in foods:
        board[board_index(food)] = CellValue.FOOD

    return GameState(
        board=board,
        snake=snake,
        direction=direction,
        foods=tuple(foods),
        score=score,
        is_game_over=False,
    )

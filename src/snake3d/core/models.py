from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Mapping


class CellValue(IntEnum):
    EMPTY = 0
    HEAD = 1
    BODY = 2
    FOOD = 3


@dataclass(frozen=True, slots=True)
class Coord:
    x: int
    y: int
    z: int

    def moved(self, direction: Direction) -> Coord:
        return Coord(
            self.x + direction.dx, self.y + direction.dy, self.z + direction.dz
        )

    def as_tuple(self) -> tuple[int, int, int]:
        return (self.x, self.y, self.z)


@dataclass(frozen=True, slots=True)
class Direction:
    dx: int
    dy: int
    dz: int

    def is_opposite(self, other: Direction) -> bool:
        return (self.dx, self.dy, self.dz) == (-other.dx, -other.dy, -other.dz)

    def as_tuple(self) -> tuple[int, int, int]:
        return (self.dx, self.dy, self.dz)


LEFT = Direction(-1, 0, 0)
RIGHT = Direction(1, 0, 0)
UP = Direction(0, -1, 0)
DOWN = Direction(0, 1, 0)
ASCEND = Direction(0, 0, 1)
DESCEND = Direction(0, 0, -1)


@dataclass(frozen=True, slots=True)
class ControlMapping:
    forward: str = "w"
    backward: str = "s"
    left: str = "a"
    right: str = "d"
    ascend: str = "e"
    descend: str = "q"
    pause: str = "p"
    restart: str = "n"
    quit: str = "c"

    def horizontal_direction_by_key(self) -> Mapping[str, Direction]:
        return {
            self.forward: UP,
            self.backward: DOWN,
            self.left: LEFT,
            self.right: RIGHT,
        }

    def vertical_direction_by_key(self) -> Mapping[str, Direction]:
        return {
            self.ascend: ASCEND,
            self.descend: DESCEND,
            "x": ASCEND,
            "z": DESCEND,
        }


@dataclass(frozen=True, slots=True)
class GameConfig:
    width: int = 8
    height: int = 8
    depth: int = 8
    tick_rate_hz: float = 6.0
    fruit_count: int = 3
    controls: ControlMapping = field(default_factory=ControlMapping)

    def __post_init__(self) -> None:
        if min(self.width, self.height, self.depth) < 4:
            raise ValueError("All board dimensions must be at least 4.")
        if self.tick_rate_hz <= 0:
            raise ValueError("tick_rate_hz must be positive.")
        if self.fruit_count < 1:
            raise ValueError("fruit_count must be at least 1.")

    @property
    def board_shape(self) -> tuple[int, int, int]:
        return (self.depth, self.height, self.width)

    def contains(self, coord: Coord) -> bool:
        return (
            0 <= coord.x < self.width
            and 0 <= coord.y < self.height
            and 0 <= coord.z < self.depth
        )

    def center(self) -> Coord:
        return Coord(self.width // 2, self.height // 2, self.depth // 2)

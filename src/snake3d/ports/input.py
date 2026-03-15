from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Protocol

from snake3d.core.models import Direction


class InputActionType(Enum):
    DIRECTION = auto()
    PAUSE = auto()
    RESTART = auto()
    QUIT = auto()


@dataclass(frozen=True, slots=True)
class InputAction:
    kind: InputActionType
    direction: Direction | None = None


class InputProvider(Protocol):
    def poll_action(self) -> InputAction | None: ...

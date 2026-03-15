from __future__ import annotations

from typing import Protocol

from snake3d.core.state import GameState


class Renderer(Protocol):
    def initialize(self) -> None: ...

    def build_frame(self, state: GameState) -> str: ...

    def render(self, state: GameState) -> None: ...

    def shutdown(self) -> None: ...

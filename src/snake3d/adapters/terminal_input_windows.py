from __future__ import annotations

import os

from snake3d.core.models import ControlMapping
from snake3d.ports.input import InputAction, InputActionType

try:
    import msvcrt
except ImportError:  # pragma: no cover - exercised only on non-Windows import paths.
    msvcrt = None


class WindowsTerminalInput:
    def __init__(self, controls: ControlMapping) -> None:
        self.controls = controls
        self._direction_keys = controls.direction_by_key()
        if os.name != "nt" or msvcrt is None:
            raise RuntimeError(
                "WindowsTerminalInput is supported only on Windows terminals."
            )

    def poll_action(self) -> InputAction | None:
        if not msvcrt.kbhit():
            return None

        key = msvcrt.getwch().lower()
        if key in self._direction_keys:
            return InputAction(InputActionType.DIRECTION, self._direction_keys[key])
        if key == self.controls.pause:
            return InputAction(InputActionType.PAUSE)
        if key == self.controls.restart:
            return InputAction(InputActionType.RESTART)
        if key == self.controls.quit:
            return InputAction(InputActionType.QUIT)
        return None

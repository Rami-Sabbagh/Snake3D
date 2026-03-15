from __future__ import annotations

import os
import time

from snake3d.core.models import ControlMapping
from snake3d.ports.input import InputAction, InputActionType

try:
    import msvcrt
except ImportError:  # pragma: no cover - exercised only on non-Windows import paths.
    msvcrt = None


class WindowsTerminalInput:
    def __init__(self, controls: ControlMapping) -> None:
        self.controls = controls
        self._horizontal_keys = controls.horizontal_direction_by_key()
        self._vertical_keys = controls.vertical_direction_by_key()
        self._extended_horizontal_keys = {
            "ext:h": self._horizontal_keys[controls.forward],
            "ext:p": self._horizontal_keys[controls.backward],
            "ext:k": self._horizontal_keys[controls.left],
            "ext:m": self._horizontal_keys[controls.right],
        }
        self._last_vertical_key: str | None = None
        self._last_vertical_time = 0.0
        self._vertical_repeat_guard_seconds = 0.18
        if os.name != "nt" or msvcrt is None:
            raise RuntimeError(
                "WindowsTerminalInput is supported only on Windows terminals."
            )

    def _read_key(self) -> str | None:
        if not msvcrt.kbhit():
            return None

        key = msvcrt.getwch()
        if key in ("\x00", "\xe0"):
            return f"ext:{msvcrt.getwch().lower()}"
        if key == "\x1b":
            return "esc"
        return key.lower()

    def _is_repeated_vertical_hold(self, key: str) -> bool:
        now = time.monotonic()
        repeated = (
            key == self._last_vertical_key
            and (now - self._last_vertical_time) < self._vertical_repeat_guard_seconds
        )
        self._last_vertical_key = key
        self._last_vertical_time = now
        return repeated

    def poll_action(self) -> InputAction | None:
        key = self._read_key()
        if key is None:
            return None

        if key in self._horizontal_keys:
            self._last_vertical_key = None
            return InputAction(InputActionType.DIRECTION, self._horizontal_keys[key])
        if key in self._extended_horizontal_keys:
            self._last_vertical_key = None
            return InputAction(
                InputActionType.DIRECTION, self._extended_horizontal_keys[key]
            )
        if key in self._vertical_keys:
            if self._is_repeated_vertical_hold(key):
                return None
            return InputAction(InputActionType.VERTICAL, self._vertical_keys[key])
        if key == self.controls.pause:
            return InputAction(InputActionType.PAUSE)
        if key == self.controls.restart:
            return InputAction(InputActionType.RESTART)
        if key == self.controls.quit or key == "esc":
            return InputAction(InputActionType.QUIT)
        return None

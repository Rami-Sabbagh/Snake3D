"""Terminal input provider using xterm escape sequences."""

import select
import sys
import termios
import tty
from collections.abc import Mapping
from typing import Any, TextIO

from snake3d.core.models import Direction, GameConfig
from snake3d.ports.input import InputAction, InputActionType


class TerminalInputProvider:
    """Input provider that reads keyboard input using xterm escape sequences.

    Uses raw terminal mode and non-blocking input to poll for key presses
    without blocking the main game loop. Supports standard ASCII keys and
    xterm arrow key sequences.
    """

    def __init__(
        self,
        config: GameConfig,
        *,
        input_stream: TextIO = sys.stdin,
    ) -> None:
        self.config = config
        self.input_stream = input_stream
        self._original_terminal_settings: Any = None
        self._initialize_terminal()

        # Build key mappings
        self._horizontal_keys = config.controls.horizontal_direction_by_key()
        self._vertical_keys = config.controls.vertical_direction_by_key()

        # Common xterm arrow key sequences
        self._arrow_keys: Mapping[str, Direction] = {
            "\x1b[A": self._horizontal_keys.get("w", Direction(0, -1, 0)),  # Up arrow
            "\x1b[B": self._horizontal_keys.get("s", Direction(0, 1, 0)),  # Down arrow
            "\x1b[C": self._horizontal_keys.get("d", Direction(1, 0, 0)),  # Right arrow
            "\x1b[D": self._horizontal_keys.get("a", Direction(-1, 0, 0)),  # Left arrow
        }

    def _initialize_terminal(self) -> None:
        """Set terminal to raw mode for character-by-character input."""
        if not self.input_stream.isatty():
            return

        fd = self.input_stream.fileno()
        try:
            self._original_terminal_settings = termios.tcgetattr(fd)
            tty.setraw(fd)
        except (termios.error, OSError):
            # If we can't set raw mode, continue without it
            self._original_terminal_settings = None

    def _read_available_input(self) -> str:
        """Read all available input without blocking."""
        # For non-TTY streams (like StringIO in tests), try to read directly
        if not self.input_stream.isatty():
            # Try to read without blocking
            try:
                char = self.input_stream.read(1)
                return char if char else ""
            except (OSError, ValueError):
                return ""

        fd = self.input_stream.fileno()
        chars: list[str] = []

        # Use select to check if input is available
        while True:
            readable, _, _ = select.select([fd], [], [], 0)
            if not readable:
                break

            try:
                char = self.input_stream.read(1)
                if not char:
                    break
                chars.append(char)

                # For escape sequences, try to read the full sequence
                # Most xterm sequences are 3 characters like \x1b[A
                if char == "\x1b" and len(chars) < 3:
                    continue
            except OSError:
                break

        return "".join(chars)

    def poll_action(self) -> InputAction | None:
        """Poll for input and return the corresponding action."""
        input_text = self._read_available_input()
        if not input_text:
            return None

        # Check for escape sequences (arrow keys)
        if input_text in self._arrow_keys:
            direction = self._arrow_keys[input_text]
            return InputAction(kind=InputActionType.DIRECTION, direction=direction)

        # For multi-character input, process only the first character
        # (in case of buffered input)
        key = input_text[0].lower()

        # Check pause
        if key == self.config.controls.pause.lower():
            return InputAction(kind=InputActionType.PAUSE)

        # Check restart
        if key == self.config.controls.restart.lower():
            return InputAction(kind=InputActionType.RESTART)

        # Check quit (also support Ctrl+C as \x03)
        if key == self.config.controls.quit.lower() or input_text == "\x03":
            return InputAction(kind=InputActionType.QUIT)

        # Check horizontal directions
        if key in self._horizontal_keys:
            return InputAction(kind=InputActionType.DIRECTION, direction=self._horizontal_keys[key])

        # Check vertical directions
        if key in self._vertical_keys:
            return InputAction(kind=InputActionType.VERTICAL, direction=self._vertical_keys[key])

        # Unknown key, return None
        return None

    def shutdown(self) -> None:
        """Restore terminal to original settings."""
        if self._original_terminal_settings is None:
            return

        fd = self.input_stream.fileno()
        try:
            termios.tcsetattr(fd, termios.TCSADRAIN, self._original_terminal_settings)
        except (termios.error, OSError):
            pass

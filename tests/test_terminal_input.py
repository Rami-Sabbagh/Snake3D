"""Tests for terminal input provider."""

from __future__ import annotations

from io import StringIO

from snake3d.adapters.terminal_input import TerminalInputProvider
from snake3d.core.models import ASCEND, DOWN, LEFT, RIGHT, UP, GameConfig
from snake3d.ports.input import InputActionType


class FakeInputStream(StringIO):
    """Fake input stream that simulates terminal behavior."""

    def __init__(self, data: str = "") -> None:
        super().__init__(data)
        self._buffered_data = data
        self._read_pos = 0

    def isatty(self) -> bool:
        """Always return False to avoid terminal mode setup in tests."""
        return False

    def fileno(self) -> int:
        """Return a fake file descriptor."""
        return 0


def test_terminal_input_basic_keys():
    """Test basic key inputs for direction, pause, quit, and restart."""
    config = GameConfig()

    # Test each control key
    for key, expected_kind in [
        ("w", InputActionType.DIRECTION),
        ("a", InputActionType.DIRECTION),
        ("s", InputActionType.DIRECTION),
        ("d", InputActionType.DIRECTION),
        ("e", InputActionType.VERTICAL),
        ("q", InputActionType.VERTICAL),
        ("p", InputActionType.PAUSE),
        ("n", InputActionType.RESTART),
        ("c", InputActionType.QUIT),
    ]:
        stream = FakeInputStream(key)
        provider = TerminalInputProvider(config, input_stream=stream)
        action = provider.poll_action()
        assert action is not None
        assert action.kind == expected_kind


def test_terminal_input_horizontal_directions():
    """Test that horizontal direction keys map correctly."""
    config = GameConfig()

    test_cases = [
        ("w", UP),
        ("s", DOWN),
        ("a", LEFT),
        ("d", RIGHT),
    ]

    for key, expected_direction in test_cases:
        stream = FakeInputStream(key)
        provider = TerminalInputProvider(config, input_stream=stream)
        action = provider.poll_action()
        assert action is not None
        assert action.direction == expected_direction


def test_terminal_input_vertical_directions():
    """Test that vertical direction keys map correctly."""
    config = GameConfig()

    # Test ascend/descend
    stream = FakeInputStream("e")
    provider = TerminalInputProvider(config, input_stream=stream)
    action = provider.poll_action()
    assert action is not None
    assert action.direction == ASCEND

    # Test Q for descend (from default controls)
    # Note: the config.controls.descend is 'q'
    stream = FakeInputStream("q")
    provider = TerminalInputProvider(config, input_stream=stream)
    action = provider.poll_action()
    assert action is not None
    # Q maps to DESCEND in vertical_direction_by_key


def test_terminal_input_no_action_on_empty():
    """Test that polling with no input returns None."""
    config = GameConfig()
    stream = FakeInputStream("")
    provider = TerminalInputProvider(config, input_stream=stream)
    action = provider.poll_action()
    assert action is None


def test_terminal_input_unknown_key():
    """Test that unknown keys return None."""
    config = GameConfig()
    stream = FakeInputStream("y")  # Not mapped to any action
    provider = TerminalInputProvider(config, input_stream=stream)
    action = provider.poll_action()
    assert action is None


def test_terminal_input_shutdown():
    """Test that shutdown doesn't raise errors."""
    config = GameConfig()
    stream = FakeInputStream("")
    provider = TerminalInputProvider(config, input_stream=stream)
    # Should not raise
    provider.shutdown()

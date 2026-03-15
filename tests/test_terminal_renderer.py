from __future__ import annotations

from io import StringIO

from snake3d.adapters.terminal_renderer import (
    HOME,
    HIDE_CURSOR,
    SHOW_CURSOR,
    TerminalRenderer,
)
from snake3d.core.models import Coord, GameConfig, RIGHT
from snake3d.core.state import create_state


def test_renderer_shows_three_slice_window_and_level_bar() -> None:
    config = GameConfig(width=8, height=8, depth=8)
    state = create_state(
        config,
        [Coord(3, 4, 5), Coord(2, 4, 5), Coord(1, 4, 5)],
        RIGHT,
        food=Coord(4, 5, 5),
    )
    renderer = TerminalRenderer(config, stream=StringIO())

    frame = renderer.build_frame(state)

    assert "z=4" in frame
    assert "z=5" in frame
    assert "z=6" in frame
    assert "z=3" not in frame
    assert "5 |#|" in frame
    assert "Snake3D" in frame


def test_renderer_uses_gray_placeholder_panels_for_missing_slices() -> None:
    config = GameConfig(width=8, height=8, depth=8)
    state = create_state(
        config,
        [Coord(3, 3, 0), Coord(2, 3, 0), Coord(1, 3, 0)],
        RIGHT,
        food=Coord(5, 5, 0),
    )
    renderer = TerminalRenderer(config, stream=StringIO())

    frame = renderer.build_frame(state)

    assert "z=--" in frame
    assert "\x1b[90m" in frame
    assert "0 |#|" in frame


def test_renderer_writes_terminal_control_sequences_on_render_and_shutdown() -> None:
    config = GameConfig(width=8, height=8, depth=8)
    state = create_state(
        config,
        [Coord(3, 3, 3), Coord(2, 3, 3), Coord(1, 3, 3)],
        RIGHT,
        food=Coord(5, 5, 5),
    )
    stream = StringIO()
    renderer = TerminalRenderer(config, stream=stream)

    renderer.initialize()
    renderer.render(state)
    renderer.shutdown()

    output = stream.getvalue()
    assert HIDE_CURSOR in output
    assert HOME in output
    assert SHOW_CURSOR in output

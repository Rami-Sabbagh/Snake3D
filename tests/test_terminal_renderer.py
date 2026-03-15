from __future__ import annotations

import re
from io import StringIO

from snake3d.adapters.terminal_renderer import (
    HOME,
    HIDE_CURSOR,
    SHOW_CURSOR,
    TerminalRenderer,
)
from snake3d.core.models import Coord, GameConfig, RIGHT
from snake3d.core.state import create_state


ANSI_PATTERN = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")


def strip_ansi(text: str) -> str:
    return ANSI_PATTERN.sub("", text)


def test_renderer_shows_three_slice_window_and_level_bar() -> None:
    config = GameConfig(width=8, height=8, depth=8)
    state = create_state(
        config,
        [Coord(3, 4, 5), Coord(2, 4, 5), Coord(1, 4, 5)],
        RIGHT,
        foods=(Coord(4, 5, 5), Coord(1, 1, 2), Coord(2, 2, 7)),
    )
    renderer = TerminalRenderer(config, stream=StringIO())

    frame = strip_ansi(renderer.build_frame(state))

    assert "z=4" in frame
    assert "z=5" in frame
    assert "z=6" in frame
    assert "z=3" not in frame
    assert frame.count(">") == 1
    assert frame.count("*") >= 2
    assert "5|#|" not in frame
    assert "2|@|" not in frame
    assert "7|@|" not in frame
    assert "score=" in frame
    assert "Snake3D" in frame


def test_renderer_wraps_adjacent_panels_at_depth_edges() -> None:
    config = GameConfig(width=8, height=8, depth=8)
    state = create_state(
        config,
        [Coord(3, 3, 0), Coord(2, 3, 0), Coord(1, 3, 0)],
        RIGHT,
        food=Coord(5, 5, 0),
    )
    renderer = TerminalRenderer(config, stream=StringIO())

    frame = strip_ansi(renderer.build_frame(state))

    assert "z=7" in frame
    assert "z=0" in frame
    assert "z=1" in frame
    assert "z=--" not in frame
    assert frame.count(">") == 1


def test_renderer_uses_at_sign_for_food_with_default_glyphs() -> None:
    config = GameConfig(width=8, height=8, depth=8)
    state = create_state(
        config,
        [Coord(3, 3, 3), Coord(2, 3, 3), Coord(1, 3, 3)],
        RIGHT,
        food=Coord(5, 5, 5),
    )
    renderer = TerminalRenderer(config, stream=StringIO())

    frame = strip_ansi(renderer.build_frame(state))

    assert "@=food" in frame


def test_renderer_uses_nerd_font_depth_indicator_when_enabled() -> None:
    config = GameConfig(width=8, height=8, depth=8)
    state = create_state(
        config,
        [Coord(3, 3, 3), Coord(2, 3, 3), Coord(1, 3, 3)],
        RIGHT,
        foods=(Coord(5, 5, 5), Coord(1, 1, 7)),
    )
    renderer = TerminalRenderer(config, stream=StringIO(), use_nerd_font=True)

    frame = strip_ansi(renderer.build_frame(state))

    assert "󰍉=head" in frame
    assert "" in frame
    assert "󰓣" in frame


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

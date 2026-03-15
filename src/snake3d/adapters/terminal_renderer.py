from __future__ import annotations

import sys
from typing import TextIO

from colorama import just_fix_windows_console

from snake3d.adapters.terminal_size import detect_terminal_size
from snake3d.core.models import CellValue, Coord, GameConfig
from snake3d.core.state import GameState, board_index

RESET = "\x1b[0m"
DIM = "\x1b[2m"
GRAY = "\x1b[90m"
GREEN = "\x1b[32m"
BRIGHT_GREEN = "\x1b[92m"
RED = "\x1b[31m"
BOLD = "\x1b[1m"
HIDE_CURSOR = "\x1b[?25l"
SHOW_CURSOR = "\x1b[?25h"
HOME = "\x1b[H"
CLEAR = "\x1b[2J"
CLEAR_TO_END = "\x1b[J"


class TerminalRenderer:
    def __init__(self, config: GameConfig, stream: TextIO | None = None) -> None:
        self.config = config
        self.stream = stream if stream is not None else sys.stdout
        self._initialized = False

    def initialize(self) -> None:
        just_fix_windows_console()
        self.stream.write(HIDE_CURSOR + CLEAR + HOME)
        self.stream.flush()
        self._initialized = True

    def _render_cell(self, coord: Coord, state: GameState) -> str:
        cell = CellValue(int(state.board[board_index(coord)]))
        if cell is CellValue.HEAD:
            return f"{BRIGHT_GREEN}O{RESET}"
        if cell is CellValue.BODY:
            return f"{GREEN}o{RESET}"
        if cell is CellValue.FOOD:
            return f"{RED}*{RESET}"
        return f"{DIM}.{RESET}"

    def _panel_label(self, z_level: int | None) -> str:
        return f"z={z_level}" if z_level is not None else "z=--"

    def _panel_lines(self, state: GameState, z_level: int | None) -> list[str]:
        lines = [self._panel_label(z_level)]
        if z_level is None:
            placeholder = " ".join(["."] * self.config.width)
            lines.extend(
                [f"{GRAY}{placeholder}{RESET}" for _ in range(self.config.height)]
            )
            return lines

        for y in range(self.config.height):
            cells = [
                self._render_cell(Coord(x, y, z_level), state)
                for x in range(self.config.width)
            ]
            lines.append(" ".join(cells))
        return lines

    def _level_bar_lines(self, current_z: int) -> list[str]:
        lines = ["levels"]
        for z_level in range(self.config.depth):
            marker = "#" if z_level == current_z else " "
            lines.append(f"{z_level} |{marker}|")
        return lines

    def build_frame(self, state: GameState) -> str:
        size = detect_terminal_size()
        minimum_columns = (self.config.width * 2 - 1) * 3 + 20
        minimum_lines = self.config.height + 5
        if size.columns < minimum_columns or size.lines < minimum_lines:
            return (
                f"{BOLD}Snake3D{RESET} terminal too small\n"
                f"Need at least {minimum_columns}x{minimum_lines}, detected {size.columns}x{size.lines}.\n"
                "Resize the terminal and restart or continue with a larger window."
            )

        current_z = state.head.z
        panel_levels: list[int | None] = [
            current_z - 1 if current_z - 1 >= 0 else None,
            current_z,
            current_z + 1 if current_z + 1 < self.config.depth else None,
        ]
        panels = [self._panel_lines(state, level) for level in panel_levels]
        level_bar = self._level_bar_lines(current_z)
        row_count = max(len(level_bar), len(panels[0]), len(panels[1]), len(panels[2]))

        lines = [
            (
                f"{BOLD}Snake3D{RESET}  score={state.score:02d}  "
                f"dir={state.direction.as_tuple()}  head={state.head.as_tuple()}  "
                f"grid={self.config.width}x{self.config.height}x{self.config.depth}"
            ),
            "",
        ]

        for row in range(row_count):
            left = panels[0][row] if row < len(panels[0]) else ""
            middle = panels[1][row] if row < len(panels[1]) else ""
            right = panels[2][row] if row < len(panels[2]) else ""
            bar = level_bar[row] if row < len(level_bar) else ""
            lines.append(f"{left:<28}  {middle:<28}  {right:<28}  {bar}")

        lines.append("")
        lines.append(
            "Legend: O=head  o=body  *=food  .=empty  gray panel=out-of-range slice"
        )
        lines.append("Controls: W/A/S/D move, R/F vertical, P pause, N restart, Q quit")
        if state.is_game_over:
            lines.append(
                f"{RED}{BOLD}GAME OVER{RESET}  Press N to restart or Q to quit."
            )
        return "\n".join(lines)

    def render(self, state: GameState) -> None:
        frame = self.build_frame(state)
        self.stream.write(HOME + frame + CLEAR_TO_END)
        self.stream.flush()

    def shutdown(self) -> None:
        if not self._initialized:
            return
        self.stream.write(RESET + SHOW_CURSOR + "\n")
        self.stream.flush()
        self._initialized = False

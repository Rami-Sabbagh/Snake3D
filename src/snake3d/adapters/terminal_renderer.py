import sys
from dataclasses import dataclass
from typing import TextIO

from colorama import just_fix_windows_console


from snake3d.adapters.terminal_size import detect_terminal_size
from snake3d.core.models import CellValue, Coord, GameConfig
from snake3d.core.state import GameState, board_index

RESET = "\x1b[0m"
DIM = "\x1b[2m"
GREEN = "\x1b[32m"
BRIGHT_GREEN = "\x1b[92m"
RED = "\x1b[31m"
YELLOW = "\x1b[33m"
BLUE = "\x1b[34m"
CYAN = "\x1b[36m"
BRIGHT_BLACK = "\x1b[90m"
BRIGHT_YELLOW = "\x1b[93m"
BRIGHT_CYAN = "\x1b[96m"
BOLD = "\x1b[1m"
HIDE_CURSOR = "\x1b[?25l"
SHOW_CURSOR = "\x1b[?25h"
HOME = "\x1b[H"
CLEAR = "\x1b[2J"
CLEAR_TO_END = "\x1b[J"


@dataclass(frozen=True, slots=True)
class GlyphSet:
    head: str
    body: str
    food: str
    empty: str
    depth_current: str
    depth_food: str
    depth_empty: str


ASCII_GLYPHS = GlyphSet(
    head="O",
    body="o",
    food="@",
    empty=".",
    depth_current=">",
    depth_food="*",
    depth_empty=":",
)
NERD_FONT_GLYPHS = GlyphSet(
    head="󰍉",
    body="󰝤",
    food="󰭆",
    empty="·",
    depth_current="",
    depth_food="󰓣",
    depth_empty="",
)


class TerminalRenderer:
    def __init__(
        self,
        config: GameConfig,
        stream: TextIO | None = None,
        *,
        use_nerd_font: bool = False,
    ) -> None:
        self.config = config
        self.stream = stream if stream is not None else sys.stdout
        self.glyphs = NERD_FONT_GLYPHS if use_nerd_font else ASCII_GLYPHS
        self._initialized = False

    def initialize(self) -> None:
        just_fix_windows_console()
        self.stream.write(HIDE_CURSOR + CLEAR + HOME)
        self.stream.flush()
        self._initialized = True

    def _style(self, text: object, *codes: str) -> str:
        return f"{''.join(codes)}{text}{RESET}"

    def _format_stat(self, label: str, value: object, color: str) -> str:
        return f"{label}={self._style(value, BOLD, color)}"

    def _format_key(self, text: str) -> str:
        return self._style(text, BOLD, YELLOW)

    def _render_cell(self, coord: Coord, state: GameState) -> str:
        cell = CellValue(int(state.board[board_index(coord)]))
        if cell is CellValue.HEAD:
            return f"{BRIGHT_GREEN}{self.glyphs.head}{RESET}"
        if cell is CellValue.BODY:
            return f"{GREEN}{self.glyphs.body}{RESET}"
        if cell is CellValue.FOOD:
            return f"{RED}{self.glyphs.food}{RESET}"
        return f"{DIM}{self.glyphs.empty}{RESET}"

    def _panel_label(self, z_level: int, current_z: int) -> str:
        if z_level == current_z:
            return self._style(f"z={z_level}", BOLD, BRIGHT_CYAN)
        return self._style(f"z={z_level}", DIM, CYAN)

    def _panel_lines(self, state: GameState, z_level: int, current_z: int) -> list[str]:
        lines = [self._panel_label(z_level, current_z)]
        for y in range(self.config.height):
            cells = [
                self._render_cell(Coord(x, y, z_level), state)
                for x in range(self.config.width)
            ]
            lines.append(" ".join(cells))
        return lines

    def _level_bar_lines(self, state: GameState, current_z: int) -> list[str]:
        fruit_levels: set[int] = set()
        for food in state.foods:
            fruit_levels.add(food.z)

        lines = [self._style("depth", DIM, BLUE)]
        for z_level in range(self.config.depth):
            if z_level == current_z:
                lines.append(self._style(self.glyphs.depth_current, BOLD, BRIGHT_CYAN))
            elif z_level in fruit_levels:
                lines.append(self._style(self.glyphs.depth_food, BOLD, RED))
            else:
                lines.append(self._style(self.glyphs.depth_empty, BRIGHT_BLACK))
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
        panel_levels: list[int] = [
            (current_z - 1) % self.config.depth,
            current_z,
            (current_z + 1) % self.config.depth,
        ]
        panels = [self._panel_lines(state, level, current_z) for level in panel_levels]
        level_bar = self._level_bar_lines(state, current_z)
        row_count = max(len(level_bar), len(panels[0]), len(panels[1]), len(panels[2]))

        lines = [
            (
                f"{BOLD}Snake3D{RESET}  "
                f"{self._format_stat('score', f'{state.score:02d}', BRIGHT_YELLOW)}  "
                f"{self._format_stat('dir', state.direction.as_tuple(), CYAN)}  "
                f"{self._format_stat('head', state.head.as_tuple(), BRIGHT_GREEN)}  "
                f"{self._format_stat('grid', f'{self.config.width}x{self.config.height}x{self.config.depth}', BLUE)}"
            ),
            "",
        ]

        for row in range(row_count):
            left = panels[0][row] if row < len(panels[0]) else ""
            middle = panels[1][row] if row < len(panels[1]) else ""
            right = panels[2][row] if row < len(panels[2]) else ""
            bar = level_bar[row] if row < len(level_bar) else ""
            lines.append(f"{left}  {middle}  {right}  {bar}")

        lines.append("")
        lines.append(
            f"Legend: {self.glyphs.head}=head  {self.glyphs.body}=body  {self.glyphs.food}=food  {self.glyphs.empty}=empty"
        )
        lines.append(
            "Controls: "
            f"{self._format_key('W/A/S/D')} or {self._format_key('arrows')} move, "
            f"{self._format_key('E/Q')} and {self._format_key('X/Z')} shift level once, "
            f"{self._format_key('P')} pause, {self._format_key('N')} restart, "
            f"{self._format_key('C')} or {self._format_key('Esc')} quit"
        )
        if state.is_game_over:
            lines.append(
                f"{RED}{BOLD}GAME OVER{RESET}  Press N to restart or C/Esc to quit."
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

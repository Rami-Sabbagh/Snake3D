from __future__ import annotations

import os
import shutil


def detect_terminal_size() -> os.terminal_size:
    columns = os.getenv("COLUMNS")
    lines = os.getenv("LINES")
    if columns and lines and columns.isdigit() and lines.isdigit():
        return os.terminal_size((int(columns), int(lines)))
    return shutil.get_terminal_size(fallback=(120, 40))

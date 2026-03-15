# Snake3D

Snake3D is a terminal-first 3D spin on classic snake. Guide a cube-hopping snake through a wraparound arena, climb levels with one-shot vertical moves, and track depth with a dedicated side bar. The project ships with a NumPy-backed game core, ANSI terminal renderer, and an optional Pyodide-powered browser client.

## Features

- 3D wraparound grid: move freely across X/Y/Z with edges that loop around instead of walls.
- Configurable runs: pick grid size, tick speed, fruit count, and glyph set at startup.
- Rich terminal view: three adjacent depth slices plus a depth bar that highlights fruit locations.
- Flexible visuals: ASCII glyphs by default, with Nerd Font icons for a fancier look.
- Responsive controls: horizontal movement on WASD/arrows and single-tap vertical shifts, with pause/restart/quit hotkeys.
- Web play option: launch `poetry run snake3d-web` to use the Pyodide terminal client in your browser.
- Tested core: deterministic NumPy engine with unit coverage for movement, rendering, and lifecycle.

## Controls

- `W` / `A` / `S` / `D` or arrow keys: move along X/Y axes
- `E` / `Q` or `X` / `Z`: move up or down one level on the Z axis
- `P`: pause or resume
- `N`: restart
- `C` or `Esc`: quit

At startup, Snake3D prompts for:

- Grid size in `WxHxD` format (default `8x8x8`)
- Tick speed in ticks per second (default `6.0`)
- Fruit count (default `3`)
- Whether to enable NerdFont fancy glyphs for rendering

## Development

Install dependencies with Poetry and run the tests:

```powershell
poetry install
poetry run pytest
```

Run the game:

```powershell
poetry run snake3d
```

## Web version

```powershell
py -m http.server -d dist
```

Then open `http://127.0.0.1:8000/web/index.html` if your browser does not open automatically.

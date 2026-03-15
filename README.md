# Snake3D

Snake3D is a terminal 3D snake game with a NumPy-backed game core and a replaceable ANSI renderer.

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

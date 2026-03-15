# Snake3D

Snake3D is a terminal 3D snake game with a NumPy-backed game core and a replaceable ANSI renderer.

## Controls

- `W` / `S`: move along the Y axis
- `A` / `D`: move along the X axis
- `R` / `F`: move up or down on the Z axis
- `P`: pause or resume
- `N`: restart
- `Q`: quit

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
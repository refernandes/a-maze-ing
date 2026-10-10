*This project has been created as part of the 42 curriculum by rfernan, phkaway-.*

# A-Maze-ing

## Description

A-Maze-ing generates a maze from a text configuration file, displays it in a
terminal and saves it as hexadecimal wall values. It supports a perfect maze
and a connected Pac-Man board. The reusable `MazeGenerator` class is provided
as the installable `mazegen` Python module.

## Instructions

Requirements: Python 3.10 or newer, `venv`, and a Unix-like terminal for the
interactive display. Create an environment and install the development tools:

```sh
python3 -m venv .venv
source .venv/bin/activate
make install
```

Run the default board, which uses Pac-Man mode:

```sh
python3 a_maze_ing.py config.txt
```

In an interactive terminal, use `R` to regenerate, `S` to show or hide the
shortest path, `C` to change wall colours, and `Q` or `Esc` to quit. Without an
interactive terminal, the program prints an ASCII view. The generated file is
written to the filename in `OUTPUT_FILE`. It must be in the current working
directory and cannot replace a configuration, source or package file.

Run the required style and type checks or rebuild the Python distributions:

```sh
make lint
make build
```

### Configuration format

Use one `KEY=VALUE` pair per line. Lines beginning with `#` and blank lines
are ignored. These six keys are required:

| Key | Meaning | Example |
|---|---|---|
| `WIDTH` | Number of columns | `WIDTH=20` |
| `HEIGHT` | Number of rows | `HEIGHT=15` |
| `ENTRY` | Start cell, in `x,y` order | `ENTRY=0,0` |
| `EXIT` | End cell, in `x,y` order | `EXIT=19,14` |
| `OUTPUT_FILE` | File to write | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Perfect mode toggle | `PERFECT=False` |

The submitted `config.txt` is:

```ini
# Default Pac-Man-style maze configuration
WIDTH=200
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=False
SEED=42
```

`SEED` is optional; the same seed and configuration reproduce the same first
maze. Coordinates start at zero. Entry and exit must be different cells
inside the grid. All outer walls remain closed. To avoid excessive memory use,
the generator accepts at most 100,000 cells.

## Generation and design

The generator starts every cell with its four walls closed. Iterative
depth-first search (recursive backtracking) visits the grid and opens each
passage on both neighbouring cells. A local seeded random number generator
makes results reproducible. DFS was selected because its explicit stack is
easy to follow and avoids Python's recursion limit.

With `PERFECT=True`, playable cells form a spanning tree with one route
between any two of them. With `PERFECT=False` (the default), the generator
adds safe passages to create multiple routes, keeps the board connected,
checks the corners and centre, and limits dead ends. Both modes keep the
external border closed and reject open 3 by 3 areas. The centred `42` bitmap
uses fully closed cells; it is omitted with a console message when the grid is
too small.

The output has one hexadecimal digit per cell, one row per line, a blank line,
then entry, exit and a shortest path written with `N`, `E`, `S` and `W`. The
path is found with breadth-first search.

## Reusable module

The `mazegen` package contains the reusable `MazeGenerator` class. Install the
submitted wheel with pip, then use it without importing the CLI or display:

```sh
python3 -m pip install ./mazegen-1.0.0-py3-none-any.whl
```

Then import and use the generator:

```python
from mazegen import MazeGenerator

maze = MazeGenerator(20, 15, (0, 0), (19, 14), seed=42)
maze.generate()
grid = maze.get_grid()
shortest_path = maze.get_solution_path()
maze.save_to_file("maze.txt")
```

Pass custom dimensions, entry, exit, `perfect=True` for a perfect maze, and a
seed to customize generation. `get_grid()` returns the wall-mask structure;
`get_solution_path()` returns its shortest route as coordinates.

The source distribution can be rebuilt from `pyproject.toml` and the `mazegen/`
package. The reusable code is released under the MIT License in `LICENSE.md`.

## Project structure

- `a_maze_ing.py`: command-line entry point and safe output-path handling.
- `maze_config.py`: configuration parsing and validation.
- `maze_display.py`: ASCII layout and curses controls.
- `mazegen/generator.py`: `MazeGenerator` and maze-rule validation.
- `mazegen/algorithms.py`: iterative depth-first carving.
- `mazegen/pacman.py`: dead-end removal and spawn corridors.
- `mazegen/rules.py`: shared wall and 3 by 3 checks.
- `mazegen/validation.py`: connectivity, walls, borders and mode rules.
- `mazegen/solver.py`: breadth-first shortest path and output directions.
- `mazegen/constants.py`: wall bits, movement and the 42 bitmap.

## Team and project management

- **rfernan**: configuration, maze representation, DFS generation, validation
  and reusable module.
- **phkaway-**: command-line flow, terminal controls, package build and
  documentation.

The work was planned in stages: define the configuration and wall bits, build
the generator, add the output and shortest-path solver, then add the display
and package. The plan was refined after checking the Pac-Man board rules and
the package installation requirements.

The clearest design choice was keeping generation in a reusable class and
keeping input and display in the CLI. Opening both sides of each wall made the
file format straightforward to validate. The project could improve with a
dedicated automated test suite and more recorded peer-review milestones.

## Resources

- Jamis Buck, *Mazes for Programmers*.
- Python documentation for `random`, `collections.deque` and `curses`.
- The A-Maze-ing subject and its maze analyzer.

These references informed DFS generation, breadth-first search and terminal
controls. Tools used: Python, `venv`, `flake8`, `mypy`, `build`, curses, Git and
peer review. AI assisted with design discussion, edge-case review and
documentation. Its suggestions were reviewed and adapted by the team; both
members are responsible for understanding the submitted code.

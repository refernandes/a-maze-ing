*This project has been created as part of the 42 curriculum by rfernan, phkaway-.*

# A-Maze-ing

## Description

A-Maze-ing is a Python maze generator for the 42 curriculum. It reads a plain
text configuration file, generates a random maze, displays it in an
interactive renderer, and writes the result to an output file.

Each cell is stored as one hexadecimal digit. The four bits of the digit
represent closed walls:

| Bit | Value | Direction |
|---:|---:|---|
| 0 | 1 | North |
| 1 | 2 | East |
| 2 | 4 | South |
| 3 | 8 | West |

The project supports two required modes:

- `PERFECT=True`: a connected spanning tree with no independent loops;
- `PERFECT=False`: a Pac-Man-style board with connected corridors, usable
  corners and centre, at least two independent routes, and as few dead-ends as
  possible.

The generator also reserves a visible pattern made from fully closed cells to
draw `42` whenever the configured dimensions are large enough.

The reusable generation logic is provided by the `mazegen.MazeGenerator`
package. The command-line program and the renderer use this package without
duplicating the generation algorithm.

## Requirements

- Python 3.10 or newer;
- a Unix-like terminal for the curses interface;
- Tkinter is optional and is used when a graphical display is available;
- `venv`, `build`, `flake8` and `mypy` for the complete development workflow.

The runtime generator itself uses only the Python standard library.

On Debian/Ubuntu, install Tkinter if you want the optional graphical window:

```bash
sudo apt update
sudo apt install python3-tk
```

The terminal renderer does not require Tkinter.

## Repository layout

The following files must be at the root of the submitted repository:

```text
README.md                         this documentation
a_maze_ing.py                     command-line entry point
config.txt                        default configuration
mazegen/                          reusable Python package source
pyproject.toml                    package build configuration
mazegen-*.whl                     built wheel distribution
mazegen-*.tar.gz                  built source distribution
LICENSE.md                        reusable-package license
Makefile                          development commands
docs/                             supplementary documentation and examples
```

`docs/APRESENTACAO.md` contains a short oral-presentation guide for the
defense. `docs/config_pacman.txt` is an optional second configuration example.

## Quick start

Run these commands from the repository root.

### 1. Create and activate a virtual environment

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

After activation, `python` and `pip` refer to the virtual environment. Verify
that this is true:

```bash
python --version
python -c "import sys; print(sys.executable)"
```

Upgrade pip and install the tools used by this project:

```bash
python -m pip install --upgrade pip
python -m pip install --upgrade build flake8 mypy
```

The equivalent project command is:

```bash
make install
```

Run `make install` only after activating `.venv`; it installs the development
tools through the active Python interpreter.

### 2. Run the default perfect maze

```bash
python a_maze_ing.py config.txt
```

The program:

1. parses `config.txt`;
2. creates and validates a maze;
3. writes the first maze to `maze.txt`;
4. opens the interactive renderer when a TTY or graphical display is available.

The Makefile shortcut is:

```bash
make run
```

The default configuration uses `PERFECT=True`, `SEED=42` and `ALGORITHM=DFS`.

### 3. Run the Pac-Man-style maze

```bash
python a_maze_ing.py docs/config_pacman.txt
```

This writes `docs/maze_pacman.txt` and uses `PERFECT=False`. It creates
additional routes and removes dead-ends whenever the 3x3 corridor rule allows
it.

### 4. Exit the program

In the terminal renderer, press `Q` or `Esc`.

In the Tkinter window, close the window or use the window controls.

### 5. Deactivate the virtual environment

```bash
deactivate
```

To use the project again, activate the existing environment with
`source .venv/bin/activate`; it does not need to be recreated every time.

## Interactive renderer

The program chooses the best available renderer:

1. Tkinter window when `DISPLAY`/Wayland is available and Tkinter can start;
2. curses in an interactive terminal;
3. wall-accurate static ASCII output when stdout is redirected or curses is
   unavailable.

### Controls

| Key/button | Action |
|---|---|
| `R` / Regenerate | Generate, validate and save a new maze |
| `S` / Solution | Show or hide the BFS shortest path |
| `C` / Theme | Change the wall-colour theme |
| `4` or `P` / `42` | Show or hide the isolated `42` cells |
| `Q` or `Esc` | Exit |
| Animation button | Enable/disable step animation in the Tkinter renderer |

The entry is marked `E`, the exit is marked `X`, the solution is marked `*`,
and the isolated pattern is marked `4` in the ASCII renderer.

To run without an interactive keyboard and capture a preview:

```bash
python a_maze_ing.py config.txt > preview.txt
```

The maze is still saved to the configured `OUTPUT_FILE`.

## Configuration file

The configuration contains one `KEY=VALUE` pair per line. Empty lines and
lines whose first non-space character is `#` are ignored. Keys are written in
uppercase in the delivered examples.

### Mandatory keys

```ini
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
```

| Key | Meaning | Rules |
|---|---|---|
| `WIDTH` | Number of columns | Positive integer |
| `HEIGHT` | Number of rows | Positive integer |
| `ENTRY` | Start cell | `x,y`, inside the grid |
| `EXIT` | End cell | `x,y`, inside the grid and different from entry |
| `OUTPUT_FILE` | Output path | Must not be empty |
| `PERFECT` | Generation mode | `True` or `False`, case-insensitive value |

Coordinates are zero-based and use `(x,y)` order. `ENTRY` and `EXIT` are
cells inside the grid; they are not holes in the external border. All external
walls remain closed.

### Optional keys

```ini
SEED=42
ALGORITHM=DFS
```

`SEED` is an integer. The same seed, dimensions, mode, entry, exit and
algorithm reproduce the same first maze.

`ALGORITHM` accepts:

- `DFS`: iterative depth-first search / recursive backtracker;
- `PRIM`: randomized Prim's algorithm;
- `KRUSKAL`: randomized Kruskal's algorithm using union-find.

If `ALGORITHM` is omitted, `DFS` is used.

### Configuration examples

Perfect maze:

```ini
# Reproducible perfect maze
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
ALGORITHM=DFS
```

Pac-Man-style maze:

```ini
# Reproducible multi-route board
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze_pacman.txt
PERFECT=False
SEED=42
ALGORITHM=DFS
```

### Configuration error handling

The program exits with status 1 and prints a clear error instead of a
traceback when a configuration is invalid. To check the required cases,
temporarily edit a copy of `config.txt` and run it:

```bash
cp config.txt /tmp/a-maze-ing-invalid.txt
python a_maze_ing.py /tmp/a-maze-ing-invalid.txt
```

Try each of the following independently:

1. remove a mandatory key such as `PERFECT`;
2. add a line without `=`;
3. replace `WIDTH` or `HEIGHT` with letters;
4. replace `PERFECT=True` with `PERFECT=maybe`;
5. replace `ENTRY=0,0` with `ENTRY=zero`;
6. use an out-of-bounds coordinate such as `ENTRY=999,999`;
7. use an unknown algorithm or a non-integer seed.

The parser and generator also reject non-positive dimensions, equal entry and
exit cells, and impossible Pac-Man layouts.

## Output file format

For `WIDTH=20` and `HEIGHT=15`, the output file contains:

1. exactly 15 grid lines;
2. exactly 20 hexadecimal characters per grid line;
3. one empty line;
4. the entry coordinate;
5. the exit coordinate;
6. the shortest path using `N`, `E`, `S` and `W`.

Example structure:

```text
D539553955553D517913
...
EC545457C547C6C5546E

0,0
19,14
E, E, S, E, N, E, ...
```

The path is calculated with breadth-first search after the final maze has been
generated. This is important in Pac-Man mode because braiding changes the
graph after the initial spanning tree is carved.

Every generated passage updates both sides of the shared wall. The generator
also validates wall coherence, external borders, connectivity, loops, spawn
cells and the absence of open 3x3 areas before saving.

## Maze algorithms and design choices

The generator starts with every cell set to `0xF`, meaning that all four walls
are closed. It then opens selected edges between neighbouring cells.

### DFS / recursive backtracker

DFS is the default because it is simple, fast and creates long recognisable
corridors. The implementation uses an explicit stack instead of Python
recursion, so large mazes do not depend on the recursion limit.

### Prim

Prim grows a connected region from a random frontier. It generally produces a
more branched layout than DFS.

### Kruskal

Kruskal shuffles the possible edges and uses union-find to open an edge only
when it joins two different components. This prevents cycles in
`PERFECT=True` mode.

### BFS solver

All maze movements have equal cost. BFS visits cells by distance, so the first
time it reaches the exit it has found a shortest path. The same result is used
in the output footer and in the renderer.

### Pattern `42`

The pattern is represented as a bitmap centred in the grid. Its marked cells
are set to `0xF` and excluded from the normal maze graph. If the grid is too
small, the program prints an explanatory error and omits the pattern, as
allowed by the subject.

### Pac-Man mode

When `PERFECT=False`, the generator first creates a connected maze and then
opens carefully selected dead-end walls. Each candidate opening is rolled back
if it would create an open 3x3 area. A final validator requires at least two
independent loops, reachable corners and a usable centre.

## Validation and quality checks

### Lint and type checking

With `.venv` activated:

```bash
make lint
```

This runs:

```bash
flake8 .
mypy . --warn-return-any --warn-unused-ignores \
    --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
```

For the stricter optional check:

```bash
make lint-strict
```

This runs `flake8 .` and `mypy . --strict`.

### Clean generated files

```bash
make clean
```

This removes Python caches, mypy caches, build directories and generated egg
metadata. It does not remove the submitted wheel or source distribution.

### Subject analyzer

The official subject provides `maze_analyzer.py`. If it is available next to
the repository, run it against both generated files:

```bash
python3 /path/to/maze_analyzer.py maze.txt
python3 /path/to/maze_analyzer.py docs/maze_pacman.txt
```

The expected results are coherent walls, a perfect maze with zero loops for
`maze.txt`, and a connected Pac-Man board with at least two loops and very few
dead-ends for `docs/maze_pacman.txt`.

## Build the reusable package

The package is configured in `pyproject.toml` and can be rebuilt from the
source files.

### Build wheel and source distribution

Activate `.venv`, then run:

```bash
make build
```

The equivalent command is:

```bash
python -m build --wheel --sdist --outdir .
```

The repository root must then contain files similar to:

```text
mazegen-1.0.0-py3-none-any.whl
mazegen-1.0.0.tar.gz
```

The standard isolated build may download the build backend the first time. If
the build backend is already installed and the machine is offline, use:

```bash
python -m build --no-isolation --wheel --sdist --outdir .
```

### Install and test the wheel in another virtual environment

This test deliberately runs the CLI from a directory that does not contain
the source `mazegen/` directory. That proves that the installed package, not
the checkout, is being imported.

From the repository root:

```bash
REPO_DIR="$(pwd)"
TEST_ROOT="$(mktemp -d /tmp/a-maze-ing-package-test.XXXXXX)"

python3 -m venv "$TEST_ROOT/venv"
source "$TEST_ROOT/venv/bin/activate"
python -m pip install "$REPO_DIR/mazegen-1.0.0-py3-none-any.whl"

mkdir -p "$TEST_ROOT/app"
cp "$REPO_DIR/a_maze_ing.py" "$REPO_DIR/config.txt" "$TEST_ROOT/app/"
cd "$TEST_ROOT/app"
python a_maze_ing.py config.txt
test -f maze.txt

deactivate
```

To test the source distribution instead, install the tarball in a fresh
environment:

```bash
python3 -m venv "$TEST_ROOT/sdist-venv"
source "$TEST_ROOT/sdist-venv/bin/activate"
python -m pip install "$REPO_DIR/mazegen-1.0.0.tar.gz"
python -c "import mazegen; print(mazegen.__version__)"
deactivate
```

### Use the installed reusable API

```python
from mazegen import Algorithm, MazeGenerator

generator = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit_pos=(19, 14),
    perfect=True,
    seed=42,
    algorithm=Algorithm.DFS,
)

generator.generate()
grid = generator.get_grid()
solution = generator.get_solution_path()
generator.save_to_file("output.txt")

print(len(grid), len(grid[0]))
print("solution cells:", len(solution))
```

The reusable class exposes the validated grid, the solution path and the
isolated pattern cells. It does not require the CLI or the renderer.

## Project structure

```text
a_maze_ing.py             parse config, create generator, save and launch UI
mazegen/parser.py         strict KEY=VALUE parser
mazegen/types.py          directions, bit masks and shared types
mazegen/algorithms.py     DFS, Prim and Kruskal implementations
mazegen/generator.py      MazeGenerator orchestration and validation
mazegen/pattern42.py      centred isolated 42 pattern
mazegen/solver.py         BFS shortest-path solver
mazegen/renderer.py       Tkinter, curses and ASCII renderers
```

## Team and project management

### Team roles

The submitted implementation is documented with the following responsibility
split:

- **rfernan**: configuration parser, maze representation, generation
  algorithms, BFS solver, reusable package and core validation;
- **phkaway-**: command-line integration, Tkinter/curses/ASCII renderer,
  interactive controls, packaging checks, documentation and peer review.

Both members are expected to understand the complete generation pipeline and
be able to explain the code during the defense.

### Planned work and evolution

The initial plan was to:

1. define the hexadecimal wall representation and parser;
2. implement one reliable generation algorithm;
3. add BFS and output serialization;
4. separate the generator into an installable package;
5. add the renderer and interactive controls;
6. validate the edge cases and package installation.

The plan evolved by adding Prim and Kruskal for algorithm comparison, a
Pac-Man braiding phase, strict structural validation, the `42` pattern,
Tkinter/curses fallback behaviour, animation callbacks and a separate
virtual-environment installation check.

### What worked well

- Keeping `MazeGenerator` independent from the CLI and renderer made the
  package reusable.
- Opening both sides of every passage preserved hexadecimal wall coherence.
- Using a local seeded random generator made reproduction deterministic while
  subsequent regenerations still produce new mazes.
- Validating the final grid before writing the file caught connectivity,
  border, loop and 3x3 violations early.

### What could be improved

- Add a versioned automated test suite instead of relying mainly on smoke tests
  and the subject analyzer.
- Add case-insensitive configuration key support, or document the uppercase
  key requirement even more prominently.
- Split the initial team work into smaller milestones earlier and record the
  review decisions as the project evolves.
- Add a dedicated command that runs all invalid-configuration checks at once.

### Tools used

- Python 3.10+;
- virtual environments with `venv`;
- `build`, `flake8` and `mypy`;
- `curses` and Tkinter;
- Git and terminal-based debugging;
- peer review and AI-assisted brainstorming/review.

## Resources and AI usage

Resources consulted:

- Jamis Buck, *Mazes for Programmers*;
- documentation and standard descriptions of recursive backtracking, Prim and
  Kruskal maze generation;
- Python documentation for `random`, `collections.deque`, `curses`, Tkinter
  and `setuptools`;
- the A-Maze-ing subject and its `maze_analyzer.py` validation script.

How they were used:

- maze-generation references guided the DFS, Prim and Kruskal implementations;
- Python documentation guided seeded randomness, BFS queues, terminal input,
  Tkinter drawing and package metadata;
- the subject defined the wall bits, configuration keys, output footer,
  `PERFECT` modes and validation rules;
- the analyzer was used to check wall coherence, connectivity, loops,
  dead-ends and Pac-Man spawn cells.

AI was used for brainstorming the project structure, reviewing edge cases,
checking lint/type-checking strategy and improving documentation. Generated
suggestions were manually reviewed, tested and adapted. The team must be able
to explain every algorithm and validation rule used in the submitted code.

## Makefile commands

All commands below should be run from the repository root, preferably with
`.venv` activated:

| Command | Purpose |
|---|---|
| `make install` | Install or upgrade `build`, `flake8` and `mypy` |
| `make run` | Run `a_maze_ing.py config.txt` |
| `make debug` | Launch the CLI through Python `pdb` |
| `make lint` | Run required flake8 and mypy checks |
| `make lint-strict` | Run flake8 and `mypy --strict` |
| `make build` | Create the wheel and source distribution |
| `make clean` | Remove caches and temporary build metadata |

## Troubleshooting

### `python: command not found`

Activate the environment again:

```bash
source .venv/bin/activate
```

### Tkinter cannot open a window

This is not fatal. The program falls back to curses or ASCII. On Debian/Ubuntu
install `python3-tk` as shown in the requirements section.

### The program appears to wait for input

Use a real TTY for the interactive renderer, or redirect stdout to request the
non-interactive ASCII fallback:

```bash
python a_maze_ing.py config.txt > preview.txt
```

### The `42` pattern is not visible

The pattern is intentionally omitted for grids smaller than the required
bitmap plus its margin. The program prints an explanatory message in that
case. Use at least the dimensions from `config.txt` to display it.

### Build dependencies cannot be downloaded

Install `build` and `setuptools` while online, then retry with
`--no-isolation`:

```bash
python -m pip install build setuptools wheel
python -m build --no-isolation --wheel --sdist --outdir .
```

## License

The reusable package is released under the MIT License. See
[LICENSE.md](LICENSE.md). The license permits reuse, modification and
distribution in later projects.

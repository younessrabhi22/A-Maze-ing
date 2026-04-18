*This project has been created as part of the 42 curriculum by aait-ela, yrabhi.*

---

## Description

**A-Maze-ing** is a Python maze generator and terminal visualiser.
It reads a plain-text configuration file, generates a maze using a
chosen algorithm, embeds a hidden **"42" pattern** made of fully-walled
cells, solves it with BFS, and renders everything interactively in the
terminal with colour and animation.

Key features:

- Two generation algorithms: **Recursive Backtracker (DFS)** and
  **Randomised Prim's**.
- Perfect maze mode (exactly one path between any two cells,
  `PERFECT=True`) or imperfect mode (random loops, `PERFECT=False`).
- BFS shortest-path solver — animated show/hide toggle.
- Colour-cycling walls.
- Hex output file with embedded entry, exit and solution path.
- Reusable `mazegen` package installable with `pip`.

---

## Instructions

### Requirements

- Python 3.10 or later
- `flake8`, `mypy`, `build` (installed via `make install`)

### Installation

```bash
git clone <repository-url>
cd A-Maze-ing
make install
```

### Running

```bash
make run
# or directly:
python3 a_maze_ing.py default_config.txt
python3 a_maze_ing.py my_config.txt
```

### Interactive menu

Once the maze is displayed, a menu appears:

```
==== A-Maze-ing ====
1. Re-generate a new maze
2. Show/hide path from entry to exit
3. Rotate maze colors
4. Quit
```

### Lint and type-check

```bash
make lint          # flake8 + mypy (required flags)
make lint-strict   # flake8 + mypy --strict
```

### Build the reusable pip package

```bash
# Recommended: work inside a virtual environment
python3 -m venv venv
source venv/bin/activate
pip install build
python3 -m build
# Produces:
#   dist/mazegen-1.0.0-py3-none-any.whl
#   dist/mazegen-1.0.0.tar.gz
```

### Install the package in another project

```bash
pip install dist/mazegen-1.0.0-py3-none-any.whl
# or
pip install dist/mazegen-1.0.0.tar.gz
```

### Other Makefile targets

| Target | Description |
|---|---|
| `make run` | Run the program with the default config |
| `make debug` | Run under the Python debugger (pdb) |
| `make build` | Build the pip-installable package |
| `make clean` | Remove caches and build artefacts |
| `make fclean` | `clean` + remove generated `maze.txt` |
| `make re` | `fclean` then `run` |

---

## Configuration File

The program accepts a single argument: a plain-text configuration file.

**Format rules:**

- One `KEY=VALUE` pair per line.
- Lines starting with `#` are comments and are ignored.
- The six keys below are **mandatory** — the program exits with a clear
  error message if any is missing or malformed.

| Key | Type | Description | Example |
|---|---|---|---|
| `WIDTH` | int ≥ 3 | Number of columns | `WIDTH=20` |
| `HEIGHT` | int ≥ 3 | Number of rows | `HEIGHT=15` |
| `ENTRY` | x,y | Entrance cell (0-indexed) | `ENTRY=0,0` |
| `EXIT` | x,y | Exit cell (0-indexed) | `EXIT=19,14` |
| `PERFECT` | bool | `True` = perfect maze | `PERFECT=True` |
| `OUTPUT_FILE` | str | Path of the hex output file | `OUTPUT_FILE=maze.txt` |

**Optional keys:**

| Key | Type | Default | Description |
|---|---|---|---|
| `SEED` | int | random | Seed for reproducible generation |
| `ALGO` | str | `DFS` | Algorithm: `DFS` or `PRIM` |

**Example file (`default_config.txt`):**

```
# A-Maze-ing default configuration

WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
PERFECT=True
OUTPUT_FILE=maze.txt

# Optional
ALGO=prim
SEED=42
```

**Error handling — the program catches and reports:**

- Missing mandatory key
- Line without `=` sign
- Non-integer `WIDTH`, `HEIGHT`, or `SEED`
- Non-boolean `PERFECT` value
- `ENTRY` / `EXIT` out of maze bounds
- `ENTRY` == `EXIT`
- Unreadable or missing config file
- Unwritable output file path

---

## Output File Format

After generation the maze is written to `OUTPUT_FILE`:

```
<HEIGHT rows of WIDTH uppercase hex digits>

<entry_x>,<entry_y>
<exit_x>,<exit_y>
<shortest path as N/E/S/W characters>
```

Each hex digit encodes the closed walls of one cell as a 4-bit mask:

| Bit | Direction |
|---|---|
| 0 (LSB) | North |
| 1 | East |
| 2 | South |
| 3 | West |

`1` = wall closed, `0` = wall open.
Example: `A` (binary `1010`) means East and West walls are closed.

---

## Maze Generation Algorithm

### Choice: Iterative Recursive Backtracker (DFS)

*(Randomised Prim's is also available via `ALGO=prim`.)*

### Why Recursive Backtracker?

1. **Perfect mazes guaranteed.** DFS visits every cell exactly once
   and never creates cycles, producing a spanning tree — the
   mathematical definition of a perfect maze with exactly one path
   between any two cells.

2. **Corridor width constraint met automatically.** The backtracker
   carves exactly one-cell-wide corridors by design, so no 3×3 open
   area can appear during the DFS phase. The constraint is also
   enforced in the `_add_loops` step (`PERFECT=False`) via a
   tentative-remove-and-rollback check.

3. **Iterative avoids Python recursion limits.** A naive recursive DFS
   would hit Python's default 1 000-call stack limit on large mazes.
   Using an explicit `stack` list avoids `RecursionError` entirely.

4. **Simple and auditable.** The algorithm is easy to explain and
   verify step-by-step during peer evaluation.

### The "42" pattern

Before any carving begins, cells forming the digits "4" and "2" are
pre-marked as visited. Both algorithms skip these cells, leaving them
fully walled. They appear as a visible "42" shape in the rendered maze.
If the maze is too small (width < 9 or height < 7) a warning is
printed and the pattern is omitted.

---

## Reusable `mazegen` Module

The generation logic lives in `src/mazegen/` as a standalone Python
package, fully independent of display and path-finding code.

### Quick start

```python
from mazegen import MazeGenerator

gen = MazeGenerator(width=20, height=15, perfect=True, seed=42)
grid = gen.generate()
# grid: list[list[int]] — wall bitmask per cell
# Bit 0=North, 1=East, 2=South, 3=West  (1 = wall closed)

pattern = gen.pattern_cells  # set of (x, y) tuples

# Re-generate with a different seed
gen.seed = 99
grid2 = gen.generate()
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `width` | int | — | Number of columns (≥ 3) |
| `height` | int | — | Number of rows (≥ 3) |
| `perfect` | bool | `True` | Perfect maze if True |
| `algorithm` | str | `"dfs"` | `"dfs"` or `"prim"` |
| `seed` | int \| None | `None` | Random seed |

### Accessing a solution path

The package exposes the grid only. Combine it with the solver:

```python
from mazegen import MazeGenerator
from solver.maze_data import MazeData
from solver.pathfinder import Pathfinder

gen = MazeGenerator(20, 15, seed=42)
grid = gen.generate()

maze = MazeData(grid, 20, 15, entry=(0, 0), exit=(19, 14))
path = Pathfinder(maze).solve()
print(path)   # e.g. "EESSWWNEES..."
```

### Re-building from source

```bash
python3 -m venv venv && source venv/bin/activate
pip install build
python3 -m build
# dist/mazegen-1.0.0-py3-none-any.whl
```

---

## Resources

### References

- [Maze generation — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Recursive backtracker — jamisbuck.org](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracker)
- [Randomised Prim's — jamisbuck.org](https://weblog.jamisbuck.org/2011/1/10/maze-generation-prim-s-algorithm)
- [Python `random` module](https://docs.python.org/3/library/random.html)
- [flake8 documentation](https://flake8.pycqa.org/)
- [mypy documentation](https://mypy.readthedocs.io/)
- [Python packaging guide](https://packaging.python.org/en/latest/)

### AI usage

AI (Claude by Anthropic) was used for:

- **Code review:** identifying the 3×3 open-area bug in `_add_loops`,
  the seed reuse bug in the re-generation loop, and `mypy` type errors
  in `display.py` (`Optional` vs bare `None` defaults, missing type
  hints on method parameters).
- **Import debugging:** resolving `ModuleNotFoundError` caused by
  `src/` not being on `sys.path` when running from the project root.
- **Docstring drafting:** generating Google-style docstrings that were
  reviewed and corrected by the team.

All AI-suggested code was read, understood, tested, and approved by the
team before inclusion.

---

## Team and Project Management

### Roles

| Member | Responsibilities |
|---|---|
| **aait-ela** | Maze generation (`generator.py`), reusable `mazegen` package, configuration parsing (`utils.py`), output file format, project structure and packaging |
| **yrabhi** | Terminal display (`display.py`), path-finding (`pathfinder.py`), interactive menu in `a_maze_ing.py`, README |

### Anticipated planning vs reality

**Initial plan:**

- Day 1–2: understand the subject, design data structures and module
  layout.
- Day 3–4: implement DFS generator and hex output writer.
- Day 5: terminal display and interactive menu.
- Day 6: Prim's algorithm, pip package, README.
- Day 7: testing, lint, polish.

**How it evolved:**

- The "42" pattern requirement took longer than expected. Pre-marking
  pattern cells as visited before generation was the key insight that
  kept the algorithms clean.
- The 3×3 open-area constraint for `PERFECT=False` was initially
  overlooked; it required adding a tentative-remove-and-rollback step.
- The `pyproject.toml` `src/` layout misconfiguration was discovered
  late during package build testing.
- The `show_path` toggle bug (path disappearing on colour rotation) was
  caught during manual testing and fixed by separating the toggle from
  the draw call.
- The `ModuleNotFoundError` on `make run` was the last issue fixed —
  adding `sys.path.insert(0, "src")` in `a_maze_ing.py`.

### What worked well

- Separating concerns into `MazeData`, `Pathfinder`, `HexWriter`, and
  `TerminalDisplay` made each part independently testable.
- The iterative DFS was clean to implement and easy to audit.
- BFS path-finding was correct on the first attempt.

### What could be improved

- Add `pytest` unit tests covering the generator, pathfinder, and
  config parser edge cases.
- The Prim frontier list can accumulate duplicate edges; deduplicating
  on insertion would improve performance on very large mazes.
- Add a `--validate` flag to run the provided validation script
  automatically after generation.

### Tools used

- **VS Code** with Python and Pylance extensions.
- **flake8** and **mypy** for linting and static type checking.
- **Git** for version control and collaboration.
- **Claude (Anthropic)** for code review (see AI usage section above).

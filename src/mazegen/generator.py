"""
generator.py - Reusable MazeGenerator class.

Place this file at: src/mazegen/generator.py

Supports Recursive Backtracker (DFS) and Prim's algorithm.
Generates perfect mazes (one path) or imperfect mazes (with loops).
"""

import random
import sys
from typing import Dict, List, Optional, Set, Tuple


class MazeGenerator:
    """
    Reusable maze generator supporting DFS and Prim's algorithms.

    Each cell's wall state is a 4-bit integer:
      Bit 0 (LSB) = North wall closed
      Bit 1       = East  wall closed
      Bit 2       = South wall closed
      Bit 3       = West  wall closed

    Example:
        >>> gen = MazeGenerator(20, 15, perfect=True, seed=42)
        >>> grid = gen.generate()
        >>> pattern = gen.pattern_cells   # set of (x, y) tuples
    """

    N: int = 1
    E: int = 2
    S: int = 4
    W: int = 8
    ALL_WALLS: int = 15

    # wall_bit -> (dx, dy, opposite_wall_bit)
    DIRECTIONS: Dict[int, Tuple[int, int, int]] = {
        1: (0, -1, 4),
        2: (1, 0, 8),
        4: (0, 1, 1),
        8: (-1, 0, 2),
    }

    LOOP_FACTOR: float = 0.15

    def __init__(
        self,
        width: int,
        height: int,
        perfect: bool = True,
        algorithm: str = "dfs",
        seed: Optional[int] = None,
    ) -> None:
        """
        Initialize the MazeGenerator.

        Args:
            width: Number of columns (must be >= 3).
            height: Number of rows (must be >= 3).
            perfect: True for a perfect maze (no loops).
            algorithm: 'dfs' or 'prim'.
            seed: Optional integer seed for reproducibility.
        """
        self.width = width
        self.height = height
        self.perfect = perfect
        self.algorithm = algorithm.lower()
        self.seed = seed
        self.grid: List[List[int]] = self._fresh_grid()
        self.pattern_cells: Set[Tuple[int, int]] = (
            self._get_42_pattern_cells()
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fresh_grid(self) -> List[List[int]]:
        """Return a new grid with all walls closed."""
        return [
            [self.ALL_WALLS for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def _get_42_pattern_cells(self) -> Set[Tuple[int, int]]:
        """
        Calculate the (x, y) coordinates of the '42' pattern cells.

        Returns:
            A set of (x, y) tuples. Empty if the maze is too small.
        """
        cells: Set[Tuple[int, int]] = set()

        if self.width < 9 or self.height < 7:
            print(
                "Warning: Maze is too small to display '42' pattern.",
                file=sys.stderr,
            )
            return cells

        start_x = (self.width - 7) // 2
        start_y = (self.height - 5) // 2

        pattern_offsets: List[Tuple[int, int]] = [
            # digit "4"
            (0, 0), (2, 0),
            (0, 1), (2, 1),
            (0, 2), (1, 2), (2, 2),
            (2, 3),
            (2, 4),
            # digit "2"
            (4, 0), (5, 0), (6, 0),
            (6, 1),
            (4, 2), (5, 2), (6, 2),
            (4, 3),
            (4, 4), (5, 4), (6, 4),
        ]

        for dx, dy in pattern_offsets:
            cells.add((start_x + dx, start_y + dy))

        return cells

    def _find_start(self) -> Tuple[int, int]:
        """Return the first non-pattern cell for generation start."""
        for sy in range(self.height):
            for sx in range(self.width):
                if (sx, sy) not in self.pattern_cells:
                    return (sx, sy)
        return (0, 0)

    def _has_3x3_open(self, x: int, y: int) -> bool:
        """
        Return True if any 3x3 block containing (x, y) is fully open.

        Args:
            x: Column of the recently modified cell.
            y: Row of the recently modified cell.
        """
        ox_start = max(0, x - 2)
        ox_end = min(self.width - 2, x + 1)
        oy_start = max(0, y - 2)
        oy_end = min(self.height - 2, y + 1)

        for ox in range(ox_start, ox_end):
            for oy in range(oy_start, oy_end):
                all_open = True
                for dy in range(3):
                    for dx in range(3):
                        cx2, cy2 = ox + dx, oy + dy
                        cell = self.grid[cy2][cx2]
                        if dx < 2 and (cell & self.E):
                            all_open = False
                        if dy < 2 and (cell & self.S):
                            all_open = False
                if all_open:
                    return True
        return False

    def _are_connected(
        self, x: int, y: int, nx: int, ny: int
    ) -> bool:
        """Return True if the wall between (x,y) and (nx,ny) is open."""
        dx, dy = nx - x, ny - y
        for wall, (ddx, ddy, _) in self.DIRECTIONS.items():
            if ddx == dx and ddy == dy:
                return (self.grid[y][x] & wall) == 0
        return False

    def _remove_wall(
        self, x: int, y: int, nx: int, ny: int
    ) -> None:
        """Open the passage between (x,y) and (nx,ny)."""
        dx, dy = nx - x, ny - y
        for wall, (ddx, ddy, opp) in self.DIRECTIONS.items():
            if ddx == dx and ddy == dy:
                self.grid[y][x] &= ~wall
                self.grid[ny][nx] &= ~opp
                return

    def _restore_wall(
        self, x: int, y: int, nx: int, ny: int
    ) -> None:
        """Close the passage between (x,y) and (nx,ny)."""
        dx, dy = nx - x, ny - y
        for wall, (ddx, ddy, opp) in self.DIRECTIONS.items():
            if ddx == dx and ddy == dy:
                self.grid[y][x] |= wall
                self.grid[ny][nx] |= opp
                return

    # ------------------------------------------------------------------
    # Generation algorithms
    # ------------------------------------------------------------------

    def _generate_backtracker(self) -> None:
        """
        Carve a maze using the iterative Recursive Backtracker (DFS).

        Pattern cells are pre-marked visited so they stay fully walled.
        """
        visited: Set[Tuple[int, int]] = set(self.pattern_cells)
        stack: List[Tuple[int, int]] = []

        start = self._find_start()
        visited.add(start)
        stack.append(start)

        while stack:
            cx, cy = stack[-1]
            unvisited: List[Tuple[int, int, int, int]] = []

            for wall, (dx, dy, opp) in self.DIRECTIONS.items():
                nx, ny = cx + dx, cy + dy
                if (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                    and (nx, ny) not in visited
                ):
                    unvisited.append((wall, nx, ny, opp))

            if unvisited:
                wall, nx, ny, opp = random.choice(unvisited)
                self.grid[cy][cx] &= ~wall
                self.grid[ny][nx] &= ~opp
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()

    def _generate_prim(self) -> None:
        """
        Carve a maze using Randomized Prim's algorithm.

        Produces highly branched mazes with many short dead ends.
        Pattern cells are pre-marked visited so they stay fully walled.
        """
        visited: Set[Tuple[int, int]] = set(self.pattern_cells)

        # (from_x, from_y, to_x, to_y, wall_bit, opp_wall_bit)
        frontier: List[Tuple[int, int, int, int, int, int]] = []

        def add_frontier(cx: int, cy: int) -> None:
            """Add unvisited neighbors of (cx, cy) to the frontier."""
            for wall, (dx, dy, opp) in self.DIRECTIONS.items():
                nx, ny = cx + dx, cy + dy
                if (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                    and (nx, ny) not in visited
                ):
                    frontier.append((cx, cy, nx, ny, wall, opp))

        sx, sy = self._find_start()
        visited.add((sx, sy))
        add_frontier(sx, sy)

        while frontier:
            idx = random.randrange(len(frontier))
            cx, cy, nx, ny, wall, opp = frontier.pop(idx)

            if (nx, ny) not in visited:
                self.grid[cy][cx] &= ~wall
                self.grid[ny][nx] &= ~opp
                visited.add((nx, ny))
                add_frontier(nx, ny)

    def _add_loops(self) -> None:
        """
        Randomly remove extra walls to create loops (PERFECT=False).

        Skips any removal that would create a 3x3 or larger open area.
        """
        extra = int(self.width * self.height * self.LOOP_FACTOR)
        attempts = 0
        added = 0

        while added < extra and attempts < extra * 10:
            attempts += 1
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)

            if (x, y) in self.pattern_cells:
                continue

            wall, (dx, dy, opp) = random.choice(
                list(self.DIRECTIONS.items())
            )
            nx, ny = x + dx, y + dy

            if not (0 <= nx < self.width and 0 <= ny < self.height):
                continue
            if (nx, ny) in self.pattern_cells:
                continue
            if self._are_connected(x, y, nx, ny):
                continue

            self._remove_wall(x, y, nx, ny)
            if (
                self._has_3x3_open(x, y)
                or self._has_3x3_open(nx, ny)
            ):
                self._restore_wall(x, y, nx, ny)
                continue

            added += 1

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate(self) -> List[List[int]]:
        """
        Generate and return the maze grid.

        Resets the grid on every call so successive calls with a new
        seed produce different mazes.

        Returns:
            A 2D list of ints where each value encodes closed walls.
        """
        random.seed(self.seed)
        self.grid = self._fresh_grid()

        if self.algorithm in ("dfs", "backtracker"):
            self._generate_backtracker()
        elif self.algorithm == "prim":
            self._generate_prim()
        else:
            print(
                f"Warning: Unknown algorithm '{self.algorithm}'."
                " Defaulting to DFS.",
                file=sys.stderr,
            )
            self._generate_backtracker()

        if not self.perfect:
            self._add_loops()

        return self.grid

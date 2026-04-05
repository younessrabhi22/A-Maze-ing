"""
maze_data.py - Immutable data container for a generated maze.

Place this file at: src/solver/maze_data.py
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class MazeData:
    """
    Immutable snapshot of a generated maze.

    Attributes:
        grid_result: 2D list of wall bitmasks (row-major order).
        width: Number of columns.
        height: Number of rows.
        entry: (x, y) coordinates of the maze entrance.
        exit: (x, y) coordinates of the maze exit.
    """

    grid_result: List[List[int]]
    width: int
    height: int
    entry: Tuple[int, int]
    exit: Tuple[int, int]

    def get_walls(self, x: int, y: int) -> int:
        """
        Return the wall bitmask for cell (x, y).

        Returns 15 (all walls closed) for out-of-bounds coordinates.

        Args:
            x: Column index.
            y: Row index.

        Returns:
            Wall bitmask integer (0-15).
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid_result[y][x]
        return 15

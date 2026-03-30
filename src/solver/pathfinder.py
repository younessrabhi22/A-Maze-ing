"""
pathfinder.py - BFS shortest-path solver for the maze.

Place this file at: src/solver/pathfinder.py
"""

from collections import deque
from typing import Deque, Set, Tuple

from .maze_data import MazeData


class Pathfinder:
    """
    Find the shortest path from entry to exit using Breadth-First Search.

    Args:
        maze: A MazeData instance describing the maze.
    """

    # (dx, dy, wall_bit_to_check, direction_letter)
    _MOVES = [
        (0, -1, 1, "N"),
        (1, 0, 2, "E"),
        (0, 1, 4, "S"),
        (-1, 0, 8, "W"),
    ]

    def __init__(self, maze: MazeData) -> None:
        """
        Initialize the Pathfinder.

        Args:
            maze: The maze to solve.
        """
        self.maze = maze

    def solve(self) -> str:
        """
        Find the shortest path from entry to exit.

        Returns:
            A string of direction letters (N, E, S, W).
            Returns an empty string if no path exists or entry == exit.
        """
        if self.maze.entry == self.maze.exit:
            return ""

        queue: Deque[Tuple[Tuple[int, int], str]] = deque(
            [(self.maze.entry, "")]
        )
        visited: Set[Tuple[int, int]] = {self.maze.entry}

        while queue:
            (cx, cy), path = queue.popleft()
            walls = self.maze.get_walls(cx, cy)

            for dx, dy, wall_bit, letter in self._MOVES:
                if (walls & wall_bit) == 0:
                    nx, ny = cx + dx, cy + dy
                    if (nx, ny) not in visited:
                        new_path = path + letter
                        if (nx, ny) == self.maze.exit:
                            return new_path
                        visited.add((nx, ny))
                        queue.append(((nx, ny), new_path))

        return ""

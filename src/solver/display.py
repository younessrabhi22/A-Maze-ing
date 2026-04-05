"""
display.py - Terminal display and interactive rendering of the maze.

Place this file at: src/display.py
"""

import os
import random
import time
from typing import List, Optional, Tuple

from solver.maze_data import MazeData


class TerminalDisplay:
    """
    Render a maze in the terminal using ANSI escape codes.

    Supports animated wall drawing, colour cycling, highlighted '42'
    pattern cells, and show/hide shortest path with animation.

    Args:
        maze: The MazeData to render.
        path: Solution path string (N/E/S/W characters).
        pattern_cells: List of (x, y) cells forming the '42' pattern.
    """

    def __init__(
        self,
        maze: MazeData,
        path: Optional[str] = "",
        pattern_cells: Optional[List[Tuple[int, int]]] = None,
    ) -> None:
        """
        Initialise the display.

        Args:
            maze: MazeData instance to render.
            path: Solution path string.
            pattern_cells: List of (x, y) tuples for the '42' pattern.
        """
        self.maze = maze
        self.path: str = path if path is not None else ""
        self.pattern_cells: List[Tuple[int, int]] = (
            pattern_cells if pattern_cells is not None else []
        )

        self.c_reset = "\033[0m"
        self.bg_42 = "\033[104m"

        self.WALL = "██"
        self.EMPTY = "  "
        self.path_char = "\033[33m██\033[0m"
        self.START = "\033[32m██\033[0m"
        self.EXIT_CHAR = "\033[31m██\033[0m"

        self.path_visible: bool = False

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _random_colors(self) -> Tuple[str, str]:
        """
        Return a randomly chosen (wall_color, bg_42) ANSI pair.

        Returns:
            Tuple of two ANSI escape code strings.
        """
        palettes = [
            ("\033[0;31m", "\033[106m"),
            ("\033[0;32m", "\033[105m"),
            ("\033[0;33m", "\033[103m"),
            ("\033[0;34m", "\033[102m"),
        ]
        return random.choice(palettes)

    def _draw_at(self, cx: int, cy: int, char: str) -> None:
        """
        Move the cursor to canvas position and print a character.

        Args:
            cx: Canvas column (converted to terminal column internally).
            cy: Canvas row (converted to terminal row internally).
            char: The string to print at that position.
        """
        tx = (cx * 2) + 1
        ty = cy + 1
        print(f"\033[{ty};{tx}H{char}", end="", flush=True)

    def _draw_special_points(self) -> None:
        """Draw entry (green) and exit (red) markers on the canvas."""
        ex, ey = self.maze.entry
        self._draw_at(ex * 3 + 1, ey * 3 + 1, self.START)

        xx, xy = self.maze.exit
        self._draw_at(xx * 3 + 1, xy * 3 + 1, self.EXIT_CHAR)

    def _move_to_bottom(self) -> None:
        """Move the cursor below the maze area."""
        print(f"\033[{self.maze.height * 3 + 2};1H")

    def _draw_path(
        self, visible: bool, animate: bool = False
    ) -> None:
        """
        Draw or erase the solution path on the current canvas.

        Args:
            visible: True to draw the path, False to erase it.
            animate: True to add a small delay between each step.
        """
        if not self.path:
            self._draw_special_points()
            self._move_to_bottom()
            return

        char = self.path_char if visible else self.EMPTY
        cx, cy = self.maze.entry

        for direction in self.path:
            sx, sy = cx * 3, cy * 3

            if direction == "E":
                self._draw_at(sx + 2, sy + 1, char)
                self._draw_at(sx + 3, sy + 1, char)
                cx += 1
            elif direction == "S":
                self._draw_at(sx + 1, sy + 2, char)
                self._draw_at(sx + 1, sy + 3, char)
                cy += 1
            elif direction == "W":
                if sx > 0:
                    self._draw_at(sx, sy + 1, char)
                if sx - 1 >= 0:
                    self._draw_at(sx - 1, sy + 1, char)
                cx -= 1
            elif direction == "N":
                if sy > 0:
                    self._draw_at(sx + 1, sy, char)
                if sy - 1 >= 0:
                    self._draw_at(sx + 1, sy - 1, char)
                cy -= 1

            if (
                (cx, cy) != self.maze.entry
                and (cx, cy) != self.maze.exit
            ):
                self._draw_at(cx * 3 + 1, cy * 3 + 1, char)

            if animate:
                time.sleep(0.01)

        self._draw_special_points()
        self._move_to_bottom()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def render(self, rotate_colors: bool = False) -> None:
        """
        Clear the screen and draw the entire maze.

        Re-draws the path without toggling its state so colour rotation
        does not accidentally hide a path the user has already revealed.

        Args:
            rotate_colors: If True, choose a random colour palette.
        """
        try:
            print("\033[2J\033[H", end="", flush=True)

            if rotate_colors:
                wall_color, self.bg_42 = self._random_colors()
            else:
                wall_color = "\033[37m"
                self.bg_42 = "\033[104m"

            self.WALL = f"{wall_color}██{self.c_reset}"

            for y in range(self.maze.height):
                for _ in range(3):
                    line = ""
                    for x in range(self.maze.width):
                        line += self.WALL * 3
                    print(line)

            if not rotate_colors:
                time.sleep(0.5)

            for y in range(self.maze.height):
                for x in range(self.maze.width):
                    val = self.maze.get_walls(x, y)
                    sx, sy = x * 3, y * 3

                    is_42 = (x, y) in self.pattern_cells
                    p = (
                        f"{self.bg_42}  {self.c_reset}"
                        if is_42
                        else self.EMPTY
                    )

                    self._draw_at(sx + 1, sy + 1, p)

                    if not (val & 2):        # East passage open
                        self._draw_at(sx + 2, sy + 1, p)
                        self._draw_at(sx + 3, sy + 1, p)

                    if not (val & 4):        # South passage open
                        self._draw_at(sx + 1, sy + 2, p)
                        self._draw_at(sx + 1, sy + 3, p)

                    if not rotate_colors:
                        time.sleep(0.01)

            self._draw_special_points()
            self._move_to_bottom()

            # Re-draw path without flipping the toggle state
            if self.path_visible:
                self._draw_path(visible=True, animate=False)

        except Exception:
            os.system("clear")
            print("Rendering error: could not display the maze.")

    def show_path(self) -> None:
        """
        Toggle the shortest path visibility.

        Alternates between showing and hiding the solution path without
        affecting wall colours or the maze structure.
        """
        self.path_visible = not self.path_visible
        self._draw_path(visible=self.path_visible, animate=True)

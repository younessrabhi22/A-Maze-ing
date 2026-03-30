"""
hex_writer.py - Write the maze to a file in hexadecimal wall format.

Place this file at: src/solver/hex_writer.py
"""

from .maze_data import MazeData


class HexWriter:
    """
    Write a solved maze to a text file.

    Output format:
        - HEIGHT lines of WIDTH hex digits (one digit per cell).
        - An empty line.
        - The ENTRY coordinates as 'x,y'.
        - The EXIT  coordinates as 'x,y'.
        - The shortest path as a string of N/E/S/W letters.

    Args:
        maze: The MazeData to serialise.
        path: The solution path string.
        output_path: Destination file path.
    """

    def __init__(
        self, maze: MazeData, path: str, output_path: str
    ) -> None:
        """
        Initialize HexWriter.

        Args:
            maze: MazeData containing grid, dimensions, entry and exit.
            path: Solution path string (N/E/S/W characters).
            output_path: Path of the file to create or overwrite.
        """
        self.maze = maze
        self.path = path
        self.output_path = output_path

    def _cell_hex(self, x: int, y: int) -> str:
        """Return the uppercase hex digit for cell (x, y)."""
        return format(self.maze.get_walls(x, y), "X")

    def write(self) -> None:
        """
        Write the maze to disk.

        Raises:
            OSError: If the output file cannot be created or written.
        """
        try:
            with open(self.output_path, "w") as fh:
                for y in range(self.maze.height):
                    row = "".join(
                        self._cell_hex(x, y)
                        for x in range(self.maze.width)
                    )
                    fh.write(row + "\n")

                fh.write("\n")
                fh.write(
                    f"{self.maze.entry[0]},{self.maze.entry[1]}\n"
                )
                fh.write(
                    f"{self.maze.exit[0]},{self.maze.exit[1]}\n"
                )
                fh.write(f"{self.path}\n")
        except OSError as exc:
            raise OSError(
                f"Cannot write output file"
                f" '{self.output_path}': {exc}"
            ) from exc

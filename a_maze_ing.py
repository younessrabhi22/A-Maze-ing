"""
a_maze_ing.py - Entry point for the A-Maze-ing maze generator.

Usage:
    python3 a_maze_ing.py <config.txt>
"""

import os
import random
import sys
from typing import Any, Dict, List, Set, Tuple

# Make src/ importable without installing the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from mazegen.utils import parse_config, validate_config  # noqa: E402
from mazegen.generator import MazeGenerator  # noqa: E402
from solver.hex_writer import HexWriter  # noqa: E402
from solver.maze_data import MazeData  # noqa: E402
from solver.pathfinder import Pathfinder  # noqa: E402
from solver.display import TerminalDisplay  # noqa: E402


def build_maze(
    config: Dict[str, Any],
) -> Tuple[List[List[int]], str, Set[Tuple[int, int]]]:
    """
    Generate a maze from a validated config dict and write output file.

    Args:
        config: Validated configuration dictionary.

    Returns:
        A tuple of (grid, path_string, pattern_cells).

    Raises:
        ValueError: If ENTRY or EXIT fall on a pattern cell.
        OSError: If the output file cannot be written.
    """
    gen = MazeGenerator(
        width=config["WIDTH"],
        height=config["HEIGHT"],
        perfect=config["PERFECT"],
        seed=config["SEED"],
        algorithm=config["ALGO"],
    )

    if (
        config["ENTRY"] in gen.pattern_cells
        or config["EXIT"] in gen.pattern_cells
    ):
        raise ValueError(
            "ENTRY or EXIT cannot be placed on a '42' pattern cell."
        )

    grid: List[List[int]] = gen.generate()
    pattern_cells: Set[Tuple[int, int]] = gen.pattern_cells

    entry: Tuple[int, int] = config["ENTRY"]
    exit_pt: Tuple[int, int] = config["EXIT"]

    maze_data = MazeData(
        grid, config["WIDTH"], config["HEIGHT"], entry, exit_pt
    )
    path: str = Pathfinder(maze_data).solve()

    HexWriter(maze_data, path, config["OUTPUT_FILE"]).write()

    return grid, path, pattern_cells


def main() -> None:
    """Parse config, generate maze, write file, run interactive loop."""
    if len(sys.argv) != 2:
        print(
            "Usage: python3 a_maze_ing.py <config.txt>",
            file=sys.stderr,
        )
        sys.exit(1)

    config_file: str = sys.argv[1]

    try:
        raw_config = parse_config(config_file)
        config = validate_config(raw_config)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        sys.exit(1)

    entry: Tuple[int, int] = config["ENTRY"]
    exit_pt: Tuple[int, int] = config["EXIT"]

    try:
        grid, path, pattern_cells = build_maze(config)
    except Exception as exc:
        print(f"Generation error: {exc}", file=sys.stderr)
        sys.exit(1)

    maze_obj = MazeData(
        grid, config["WIDTH"], config["HEIGHT"], entry, exit_pt
    )
    display = TerminalDisplay(maze_obj, path, list(pattern_cells))
    display.render()

    try:
        while True:
            print("\n==== A-Maze-ing ====")
            print("1. Re-generate a new maze")
            print("2. Show/hide path from entry to exit")
            print("3. Rotate maze colors")
            print("4. Quit")

            choice_raw = input("Choice (1-4): ").strip()

            try:
                choice = int(choice_raw)
            except ValueError:
                print(
                    "Invalid input, enter a number between 1 and 4."
                )
                continue

            if choice < 1 or choice > 4:
                print(
                    "Invalid input, enter a number between 1 and 4."
                )
                continue

            if choice == 1:
                os.system("clear")
                regen_config = dict(config)
                regen_config["SEED"] = random.randint(0, 2 ** 31)
                try:
                    grid, path, pattern_cells = build_maze(
                        regen_config
                    )
                except Exception as exc:
                    print(
                        f"Generation error: {exc}", file=sys.stderr
                    )
                    continue
                maze_obj = MazeData(
                    grid, config["WIDTH"], config["HEIGHT"],
                    entry, exit_pt,
                )
                display = TerminalDisplay(
                    maze_obj, path, list(pattern_cells)
                )
                display.render()

            elif choice == 2:
                display.show_path()

            elif choice == 3:
                display.render(rotate_colors=True)

            elif choice == 4:
                print("Goodbye!")
                break

    except KeyboardInterrupt:
        print("\nExiting. Goodbye!", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()

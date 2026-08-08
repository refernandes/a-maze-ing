"""A-Maze-ing: Maze generator for École 42."""
from __future__ import annotations

import sys

from mazegen.parser import parse_config
from mazegen.generator import MazeGenerator


def main() -> None:
    """Main entry point for A-Maze-ing."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        sys.exit(1)

    try:
        config = parse_config(sys.argv[1])
    except (FileNotFoundError, ValueError, OSError) as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    try:
        gen = MazeGenerator(
            width=config["width"],
            height=config["height"],
            entry=config["entry"],
            exit_pos=config["exit_pos"],
            perfect=config["perfect"],
            seed=config["seed"],
            algorithm=config["algorithm"],
        )
        gen.generate()
        gen.save_to_file(config["output_file"])
        print(f"Maze saved to {config['output_file']}")

        def regenerate() -> tuple[
            list[list[int]], list[tuple[int, int]]
        ]:
            """Regenerate maze and return new data."""
            gen.generate()
            gen.save_to_file(config["output_file"])
            return gen.get_grid(), gen.get_solution_path()

        try:
            from mazegen.renderer import MazeRenderer
            renderer = MazeRenderer(
                grid=gen.get_grid(),
                width=config["width"],
                height=config["height"],
                entry=config["entry"],
                exit_pos=config["exit_pos"],
                solution_path=gen.get_solution_path(),
                pattern_cells=gen.get_pattern_cells(),
                regenerate_callback=regenerate,
            )
            renderer.run()
        except (ImportError, RuntimeError) as exc:
            print(f"MLX unavailable: {exc}")
            print("Displaying ASCII preview instead.")
            _ascii_preview(gen)
    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(1)


def _ascii_preview(gen: MazeGenerator) -> None:
    """Print an ASCII preview of the generated maze."""
    grid = gen.get_grid()
    width = len(grid[0]) if grid else 0
    height = len(grid)
    entry = gen._entry
    exit_pos = gen._exit

    for y in range(height):
        row_str = ""
        for x in range(width):
            if (x, y) == entry:
                row_str += "E"
            elif (x, y) == exit_pos:
                row_str += "X"
            elif grid[y][x] == 15:
                row_str += "█"
            else:
                row_str += " "
        print(row_str)


if __name__ == "__main__":
    main()

"""Command-line entry point for A-Maze-ing.

The main function is intentionally thin: parse the user's configuration,
delegate all maze rules to ``MazeGenerator``, save the required file, and hand
the validated structure to ``MazeRenderer``.  Keeping UI concerns here would
make the reusable package harder to install in a future project.
"""
from __future__ import annotations

import sys
from typing import Callable

from mazegen.generator import MazeGenerator
from mazegen.parser import parse_config
from mazegen.renderer import MazeRenderer


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
            """Regenerate maze and return new grid and solution path."""
            gen.generate()
            gen.save_to_file(config["output_file"])
            return gen.get_grid(), gen.get_solution_path()

        def animated_regenerate(
            step_cb: Callable[[list[list[int]], tuple[int, int]], None]
        ) -> tuple[list[list[int]], list[tuple[int, int]]]:
            """Regenerate maze with step animation callback."""
            gen.generate(step_callback=step_cb)
            gen.save_to_file(config["output_file"])
            return gen.get_grid(), gen.get_solution_path()

        renderer = MazeRenderer(
            grid=gen.get_grid(),
            width=config["width"],
            height=config["height"],
            entry=config["entry"],
            exit_pos=config["exit_pos"],
            solution_path=gen.get_solution_path(),
            pattern_cells=gen.get_pattern_cells(),
            regenerate_callback=regenerate,
            animated_regenerate_callback=animated_regenerate,
        )
        renderer.run()
    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()

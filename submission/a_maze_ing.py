"""Command-line entry point for A-Maze-ing."""
from __future__ import annotations

from pathlib import Path
import sys

from maze_config import parse_config
from maze_display import MazeDisplay
from mazegen import MazeGenerator


def output_path(filename: str, config_filename: str) -> Path:
    """Keep output inside the working directory and protect project sources."""
    root = Path.cwd().resolve()
    requested = Path(filename)
    if (requested.is_absolute() or len(requested.parts) != 1
            or requested.name in (".", "..")):
        raise ValueError(
            "OUTPUT_FILE must be a filename in the working directory."
        )

    unresolved_target = root / requested
    if unresolved_target.is_symlink():
        raise ValueError("OUTPUT_FILE cannot be a symbolic link.")
    target = unresolved_target.resolve()
    try:
        target.relative_to(root)
    except ValueError as error:
        raise ValueError(
            "OUTPUT_FILE must resolve inside the working directory."
        ) from error

    project_root = Path(__file__).parent
    source_files = list(project_root.glob("*.py"))
    source_files.extend((project_root / "mazegen").glob("*.py"))
    project_files = (
        ".flake8", ".gitignore", "LICENSE.md", "Makefile", "README.md",
        "pyproject.toml",
    )
    protected = {
        Path(config_filename).resolve(),
        *(path.resolve() for path in source_files),
        *(project_root.joinpath(name).resolve() for name in project_files),
    }
    for pattern in ("config*.txt", "mazegen-*.whl", "mazegen-*.tar.gz"):
        protected.update(path.resolve() for path in project_root.glob(pattern))
    if target in protected:
        raise ValueError(
            "OUTPUT_FILE cannot overwrite a configuration or source file."
        )
    return target


def main() -> int:
    """Parse the one argument, generate a maze, save it and show it."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        return 1
    try:
        config = parse_config(sys.argv[1])
        destination = output_path(config.output_file, sys.argv[1])
        generator = MazeGenerator(
            config.width,
            config.height,
            config.entry,
            config.exit,
            config.perfect,
            config.seed,
        )
        generator.generate()
        generator.save_to_file(str(destination))
        print(f"Maze saved to {destination!r}")
        MazeDisplay(generator, str(destination)).run()
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

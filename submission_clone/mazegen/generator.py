"""Public maze generator and output API."""
from __future__ import annotations

import random

from mazegen.algorithms import carve_depth_first
from mazegen.constants import pattern_cells
from mazegen.pacman import open_spawn_cells, remove_dead_ends
from mazegen.solver import path_directions, shortest_path
from mazegen.validation import validate_maze

MAX_CELLS = 100_000


class MazeGenerator:
    """Generate and expose a perfect maze or Pac-Man-style board.

    Coordinates are ``(x, y)`` pairs. Grid values use one bit per closed
    wall: north 1, east 2, south 4, and west 8.
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit_pos: tuple[int, int],
        perfect: bool = False,
        seed: int | None = None,
    ) -> None:
        """Validate and retain the maze parameters."""
        if width < 1 or height < 1:
            raise ValueError("WIDTH and HEIGHT must be positive.")
        if width * height > MAX_CELLS:
            raise ValueError(f"Maze cannot exceed {MAX_CELLS} cells.")
        if entry == exit_pos:
            raise ValueError("ENTRY and EXIT must be different cells.")
        for name, point in (("ENTRY", entry), ("EXIT", exit_pos)):
            if not (0 <= point[0] < width and 0 <= point[1] < height):
                raise ValueError(f"{name} must be inside the maze.")

        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit_pos
        self.perfect = perfect
        self._random = random.Random(seed)
        self._grid: list[list[int]] = []
        self._pattern: set[tuple[int, int]] = set()

    def generate(self) -> None:
        """Generate a seeded DFS maze and enforce the project rules."""
        self._grid = [[15 for _ in range(self.width)]
                      for _ in range(self.height)]
        self._pattern = pattern_cells(self.width, self.height)
        if self.entry in self._pattern or self.exit in self._pattern:
            raise ValueError("ENTRY and EXIT cannot overlap the 42 pattern.")

        visited = carve_depth_first(
            self._grid,
            self.width,
            self.height,
            self.entry,
            self._pattern,
            self._random,
        )
        if visited != self._playable_cells():
            raise ValueError("The 42 pattern leaves unreachable maze cells.")

        if not self.perfect:
            remove_dead_ends(
                self._grid,
                self.width,
                self.height,
                self._pattern,
                self._random,
            )
            open_spawn_cells(
                self._grid,
                self.width,
                self.height,
                self._pattern,
                self._random,
            )
        validate_maze(
            self._grid,
            self.width,
            self.height,
            self.entry,
            self.perfect,
            self._pattern,
        )

    def get_grid(self) -> list[list[int]]:
        """Return a copy of the generated wall-bit grid."""
        return [row[:] for row in self._grid]

    def get_solution_path(self) -> list[tuple[int, int]]:
        """Return a shortest route as a sequence of cell coordinates."""
        return shortest_path(
            self._grid,
            self.width,
            self.height,
            self.entry,
            self.exit,
        )

    def get_pattern_cells(self) -> set[tuple[int, int]]:
        """Return a copy of the cells reserved for the 42 pattern."""
        return self._pattern.copy()

    def save_to_file(self, filename: str) -> None:
        """Write the grid, endpoints and shortest path in subject format."""
        with open(filename, "w", encoding="utf-8") as output:
            for row in self._grid:
                output.write("".join(f"{cell:X}" for cell in row) + "\n")
            output.write("\n")
            output.write(f"{self.entry[0]},{self.entry[1]}\n")
            output.write(f"{self.exit[0]},{self.exit[1]}\n")
            output.write(path_directions(self.get_solution_path()) + "\n")

    def _playable_cells(self) -> set[tuple[int, int]]:
        """Return every cell not reserved by the visible pattern."""
        return {
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) not in self._pattern
        }

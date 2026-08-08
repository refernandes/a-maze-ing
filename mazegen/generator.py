"""Main MazeGenerator class module."""
from __future__ import annotations

import random

from mazegen.algorithms import generate_dfs, generate_kruskal, generate_prim
from mazegen.pattern42 import compute_pattern_cells, stamp_pattern_42
from mazegen.solver import solve_bfs
from mazegen.types import ALL_WALLS, DELTA, OPPOSITE, Algorithm, Direction


class MazeGenerator:
    """Maze generator supporting perfect and Pac-Man style mazes."""

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit_pos: tuple[int, int],
        perfect: bool = True,
        seed: int | None = None,
        algorithm: Algorithm = Algorithm.DFS,
    ) -> None:
        """Initialize the maze generator.

        Args:
            width: Maze width.
            height: Maze height.
            entry: Entry coordinate (x, y).
            exit_pos: Exit coordinate (x, y).
            perfect: Whether to generate a perfect maze.
            seed: Random seed.
            algorithm: Algorithm to use.
        """
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive.")
        if not (0 <= entry[0] < width and 0 <= entry[1] < height):
            raise ValueError("Entry must be within bounds.")
        if not (0 <= exit_pos[0] < width and 0 <= exit_pos[1] < height):
            raise ValueError("Exit must be within bounds.")

        self._width = width
        self._height = height
        self._entry = entry
        self._exit = exit_pos
        self._perfect = perfect
        self._algorithm = algorithm
        self._rng = random.Random(seed)
        self._grid: list[list[int]] = [
            [ALL_WALLS] * width for _ in range(height)
        ]
        self._pattern_cells: set[tuple[int, int]] = set()

    def generate(self) -> None:
        """Generate the maze."""
        self._grid = [
            [ALL_WALLS] * self._width for _ in range(self._height)
        ]
        self._pattern_cells = compute_pattern_cells(
            self._width, self._height,
        )
        stamp_pattern_42(self._grid, self._pattern_cells)

        start_x, start_y = self._entry
        if self._entry in self._pattern_cells:
            for y in range(self._height):
                for x in range(self._width):
                    if (x, y) not in self._pattern_cells:
                        start_x, start_y = x, y
                        break

        if self._algorithm == Algorithm.DFS:
            generate_dfs(
                self._grid,
                self._width,
                self._height,
                start_x,
                start_y,
                self._pattern_cells,
                self._rng,
            )
        elif self._algorithm == Algorithm.PRIM:
            generate_prim(
                self._grid,
                self._width,
                self._height,
                start_x,
                start_y,
                self._pattern_cells,
                self._rng,
            )
        elif self._algorithm == Algorithm.KRUSKAL:
            generate_kruskal(
                self._grid,
                self._width,
                self._height,
                self._pattern_cells,
                self._rng,
            )

        self._open_entry_exit()

        if not self._perfect:
            self._braid()
            self._ensure_pacman_layout()

        self._validate_borders()

    def _braid(self) -> None:
        """Remove ALL dead-ends for Pac-Man/braided maze."""
        prev_count = -1
        while True:
            dead_ends: list[tuple[int, int]] = []
            for y in range(self._height):
                for x in range(self._width):
                    if (x, y) in self._pattern_cells:
                        continue
                    cell = self._grid[y][x]
                    opens = 0
                    for d in Direction:
                        if not (cell & (1 << d)):
                            dx, dy = DELTA[d]
                            nx, ny = x + dx, y + dy
                            if (
                                0 <= nx < self._width
                                and 0 <= ny < self._height
                            ):
                                opens += 1
                    if opens == 1:
                        dead_ends.append((x, y))

            if not dead_ends:
                break
            if len(dead_ends) == prev_count:
                break
            prev_count = len(dead_ends)

            for x, y in dead_ends:
                cell = self._grid[y][x]
                opens = 0
                for d in Direction:
                    if not (cell & (1 << d)):
                        dx, dy = DELTA[d]
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self._width and 0 <= ny < self._height:
                            opens += 1
                if opens != 1:
                    continue

                candidates: list[Direction] = []
                for d in Direction:
                    if cell & (1 << d):
                        dx, dy = DELTA[d]
                        nx, ny = x + dx, y + dy
                        if (
                            0 <= nx < self._width
                            and 0 <= ny < self._height
                            and (nx, ny)
                            not in self._pattern_cells
                        ):
                            candidates.append(d)

                if candidates:
                    d = self._rng.choice(candidates)
                    dx, dy = DELTA[d]
                    nx, ny = x + dx, y + dy
                    self._grid[y][x] &= ~(1 << d)
                    self._grid[ny][nx] &= ~(
                        1 << OPPOSITE[d]
                    )

    def _ensure_pacman_layout(self) -> None:
        """Ensure corners and center are open corridors."""
        corners: list[tuple[int, int]] = [
            (0, 0),
            (self._width - 1, 0),
            (0, self._height - 1),
            (self._width - 1, self._height - 1),
        ]
        center = (self._width // 2, self._height // 2)
        cells_to_check = corners + [center]

        for x, y in cells_to_check:
            if (x, y) in self._pattern_cells:
                continue
            if not (0 <= x < self._width and 0 <= y < self._height):
                continue

            cell = self._grid[y][x]
            opens = 0
            for d in Direction:
                if not (cell & (1 << d)):
                    dx, dy = DELTA[d]
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self._width and 0 <= ny < self._height:
                        opens += 1
            walls = 4 - opens

            if walls >= 2:
                candidates: list[Direction] = []
                for d in Direction:
                    if cell & (1 << d):
                        dx, dy = DELTA[d]
                        nx, ny = x + dx, y + dy
                        if (
                            0 <= nx < self._width
                            and 0 <= ny < self._height
                            and (nx, ny) not in self._pattern_cells
                        ):
                            candidates.append(d)
                if candidates:
                    d = self._rng.choice(candidates)
                    dx, dy = DELTA[d]
                    nx, ny = x + dx, y + dy
                    self._grid[y][x] &= ~(1 << d)
                    self._grid[ny][nx] &= ~(1 << OPPOSITE[d])

    def _open_entry_exit(self) -> None:
        """Open the border walls at entry and exit."""
        for cx, cy in (self._entry, self._exit):
            if cx == 0:
                self._grid[cy][cx] &= ~(1 << Direction.WEST)
            elif cx == self._width - 1:
                self._grid[cy][cx] &= ~(1 << Direction.EAST)

            if cy == 0:
                self._grid[cy][cx] &= ~(1 << Direction.NORTH)
            elif cy == self._height - 1:
                self._grid[cy][cx] &= ~(1 << Direction.SOUTH)

    def _validate_borders(self) -> None:
        """Ensure all border cells have external walls closed."""
        for x in range(self._width):
            if (x, 0) not in (self._entry, self._exit):
                self._grid[0][x] |= 1 << Direction.NORTH
            if (x, self._height - 1) not in (self._entry, self._exit):
                self._grid[self._height - 1][x] |= 1 << Direction.SOUTH

        for y in range(self._height):
            if (0, y) not in (self._entry, self._exit):
                self._grid[y][0] |= 1 << Direction.WEST
            if (self._width - 1, y) not in (self._entry, self._exit):
                self._grid[y][self._width - 1] |= 1 << Direction.EAST

    def save_to_file(self, filename: str) -> None:
        """Save maze in hex format with footer.

        Args:
            filename: Output filename.
        """
        path_str = solve_bfs(
            self._grid, self._width, self._height, self._entry, self._exit
        )
        with open(filename, "w", encoding="utf-8") as f:
            for row in self._grid:
                f.write("".join(f"{c:X}" for c in row) + "\n")
            f.write("\n")
            f.write(f"{self._entry[0]},{self._entry[1]}\n")
            f.write(f"{self._exit[0]},{self._exit[1]}\n")
            f.write(f"{path_str}\n")

    def get_grid(self) -> list[list[int]]:
        """Return a copy of the grid.

        Returns:
            A 2D array of integers.
        """
        return [row[:] for row in self._grid]

    def get_solution_path(self) -> list[tuple[int, int]]:
        """Return the BFS solution as list of (x,y) coordinates.

        Returns:
            List of coordinate tuples forming the path.
        """
        if not (
            0 <= self._entry[0] < self._width
            and 0 <= self._entry[1] < self._height
        ):
            return []
        if not (
            0 <= self._exit[0] < self._width
            and 0 <= self._exit[1] < self._height
        ):
            return []

        queue: list[tuple[int, int]] = [self._entry]
        visited: set[tuple[int, int]] = {self._entry}
        parent: dict[tuple[int, int], tuple[int, int]] = {}

        q_idx = 0
        while q_idx < len(queue):
            cx, cy = queue[q_idx]
            q_idx += 1
            if (cx, cy) == self._exit:
                break

            cell_val = self._grid[cy][cx]
            for d, (dx, dy) in DELTA.items():
                if not (cell_val & (1 << d)):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < self._width and 0 <= ny < self._height:
                        if (nx, ny) not in visited:
                            visited.add((nx, ny))
                            parent[(nx, ny)] = (cx, cy)
                            queue.append((nx, ny))

        if self._exit not in visited:
            return []

        path: list[tuple[int, int]] = []
        curr = self._exit
        while curr != self._entry:
            path.append(curr)
            curr = parent[curr]
        path.append(self._entry)
        path.reverse()
        return path

    def get_pattern_cells(self) -> set[tuple[int, int]]:
        """Return the set of '42' pattern cell coordinates.

        Returns:
            Set of (x, y) tuples.
        """
        return self._pattern_cells.copy()

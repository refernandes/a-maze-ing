"""Reusable maze generator used by both the CLI and future projects.

The public class deliberately owns the complete generation pipeline:

1. create a grid made only of closed cells;
2. reserve the isolated cells that draw ``42``;
3. carve a spanning tree with depth-first search;
4. optionally braid the tree for Pac-Man mode;
5. validate every rule before exposing or saving the result.

Keeping this orchestration in one class is important for the reusable
``mazegen`` package: a later project can use the same validated structure
without importing the command-line parser or the visualizer.
"""
from __future__ import annotations

from collections import deque
import random

from mazegen.algorithms import generate_dfs
from mazegen.pattern42 import compute_pattern_cells, stamp_pattern_42
from mazegen.solver import solve_bfs, solve_bfs_path
from mazegen.types import ALL_WALLS, DELTA, OPPOSITE, Direction


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
    ) -> None:
        """Initialize the maze generator.

        Args:
            width: Maze width.
            height: Maze height.
            entry: Entry coordinate (x, y).
            exit_pos: Exit coordinate (x, y).
            perfect: Whether to generate a perfect maze.
            seed: Random seed.
        """
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive.")
        if entry == exit_pos:
            raise ValueError("Entry and exit must be different cells.")
        if not (0 <= entry[0] < width and 0 <= entry[1] < height):
            raise ValueError("Entry must be within bounds.")
        if not (0 <= exit_pos[0] < width and 0 <= exit_pos[1] < height):
            raise ValueError("Exit must be within bounds.")

        self._width = width
        self._height = height
        self._entry = entry
        self._exit = exit_pos
        self._perfect = perfect
        self._rng = random.Random(seed)
        self._grid: list[list[int]] = [
            [ALL_WALLS] * width for _ in range(height)
        ]
        self._pattern_cells: set[tuple[int, int]] = set()

    def generate(self) -> None:
        """Generate and validate a maze.

        Every call starts from a new all-walls grid.  The local random
        generator is intentionally kept as object state, so pressing ``R``
        creates a different maze while constructing two generators with the
        same seed remains reproducible.
        """
        self._grid = [
            [ALL_WALLS] * self._width for _ in range(self._height)
        ]
        self._pattern_cells = compute_pattern_cells(
            self._width, self._height,
        )
        stamp_pattern_42(self._grid, self._pattern_cells)

        # A fully closed 42 cell is intentionally not a corridor.  Accepting
        # an entry or exit here would create a formally generated maze with no
        # valid solution, so reject the configuration with an actionable error.
        if self._entry in self._pattern_cells:
            raise ValueError("Entry cannot overlap the '42' pattern.")
        if self._exit in self._pattern_cells:
            raise ValueError("Exit cannot overlap the '42' pattern.")

        start_x, start_y = self._entry

        generate_dfs(
            self._grid,
            self._width,
            self._height,
            start_x,
            start_y,
            self._pattern_cells,
            self._rng,
        )

        if not self._perfect:
            self._braid()
            self._ensure_pacman_layout()

        # Entry and exit are cells, not holes in the outside frame.  Closing
        # all four borders matches the subject and makes the graph model
        # identical to the file representation.
        self._validate_borders()
        self._validate_generated_maze()

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
                            and (nx, ny) not in self._pattern_cells
                        ):
                            candidates.append(d)

                if candidates:
                    # Braiding is allowed to leave an occasional dead-end if
                    # every available wall would create the forbidden 3x3
                    # open area.  A valid board is more important than
                    # blindly removing the last dead-end.
                    self._rng.shuffle(candidates)
                    for d in candidates:
                        if self._try_open_edge(x, y, d):
                            break

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
                    self._rng.shuffle(candidates)
                    for d in candidates:
                        if self._try_open_edge(x, y, d):
                            break

    def _try_open_edge(
        self,
        x: int,
        y: int,
        direction: Direction,
    ) -> bool:
        """Open an edge only when it preserves the 3x3 corridor rule.

        Pac-Man braiding deliberately adds cycles, so every extra edge can
        change the shape of a nearby area.  Trying the edge temporarily and
        rolling it back makes the local constraint explicit and deterministic.
        """
        dx, dy = DELTA[direction]
        nx, ny = x + dx, y + dy
        if not (0 <= nx < self._width and 0 <= ny < self._height):
            return False
        if (nx, ny) in self._pattern_cells:
            return False

        current_bit = 1 << direction
        neighbour_bit = 1 << OPPOSITE[direction]
        old_current = self._grid[y][x]
        old_neighbour = self._grid[ny][nx]
        self._grid[y][x] &= ~current_bit
        self._grid[ny][nx] &= ~neighbour_bit
        if self._contains_open_3x3_area():
            self._grid[y][x] = old_current
            self._grid[ny][nx] = old_neighbour
            return False
        return True

    def _validate_borders(self) -> None:
        """Ensure all border cells have external walls closed."""
        for x in range(self._width):
            self._grid[0][x] |= 1 << Direction.NORTH
            self._grid[self._height - 1][x] |= 1 << Direction.SOUTH

        for y in range(self._height):
            self._grid[y][0] |= 1 << Direction.WEST
            self._grid[y][self._width - 1] |= 1 << Direction.EAST

    def _open_neighbours(self, cell: tuple[int, int]) -> list[tuple[int, int]]:
        """Return coherent, in-bounds passages leaving ``cell``.

        Checking both sides of a wall is slightly more verbose than looking
        only at the current cell, but it prevents a one-way corrupted bit from
        being mistaken for a playable corridor.
        """
        x, y = cell
        neighbours: list[tuple[int, int]] = []
        for direction, (dx, dy) in DELTA.items():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < self._width and 0 <= ny < self._height):
                continue
            if self._grid[y][x] & (1 << direction):
                continue
            if self._grid[ny][nx] & (1 << OPPOSITE[direction]):
                continue
            neighbours.append((nx, ny))
        return neighbours

    def _validate_generated_maze(self) -> None:
        """Check connectivity, walls, mode rules, and open-area limits."""
        normal_cells = {
            (x, y)
            for y in range(self._height)
            for x in range(self._width)
            if (x, y) not in self._pattern_cells
        }
        self._validate_connectivity(normal_cells)
        self._validate_wall_consistency()

        loops = self._count_loops(normal_cells)
        if self._perfect and loops != 0:
            raise ValueError("PERFECT=True requires a maze without loops.")
        if not self._perfect and loops < 2:
            raise ValueError(
                "Pac-Man mode needs at least two independent routes; "
                "the requested dimensions are too small."
            )

        if not self._perfect:
            self._validate_pacman_spawn_cells()

        if self._contains_open_3x3_area():
            raise ValueError("Generated maze contains an open 3x3 area.")

    def _validate_connectivity(
        self, normal_cells: set[tuple[int, int]]
    ) -> None:
        """Ensure every non-pattern cell can be reached from the entry.

        Args:
            normal_cells: All grid cells except the closed 42 pattern.
        """
        reachable = {self._entry}
        queue: deque[tuple[int, int]] = deque([self._entry])
        while queue:
            cell = queue.popleft()
            for neighbour in self._open_neighbours(cell):
                if neighbour not in reachable:
                    reachable.add(neighbour)
                    queue.append(neighbour)

        if reachable != normal_cells:
            missing = len(normal_cells - reachable)
            raise ValueError(
                f"Generated maze is disconnected ({missing} cell(s) "
                "cannot be reached from the entry)."
            )
        if self._exit not in reachable:
            raise ValueError("Generated maze has no path to the exit.")

    def _validate_wall_consistency(self) -> None:
        """Check that both cells sharing an edge encode the same wall."""
        for y in range(self._height):
            for x in range(self._width):
                cell_value = self._grid[y][x]
                if x + 1 < self._width:
                    east = bool(cell_value & (1 << Direction.EAST))
                    west = bool(self._grid[y][x + 1]
                                & (1 << Direction.WEST))
                    if east != west:
                        raise ValueError(
                            "Generated maze has incoherent walls."
                        )
                if y + 1 < self._height:
                    south = bool(cell_value & (1 << Direction.SOUTH))
                    north = bool(self._grid[y + 1][x]
                                 & (1 << Direction.NORTH))
                    if south != north:
                        raise ValueError(
                            "Generated maze has incoherent walls."
                        )

    def _count_loops(self, normal_cells: set[tuple[int, int]]) -> int:
        """Count independent routes in the connected maze graph.

        Args:
            normal_cells: All grid cells except the closed 42 pattern.

        Returns:
            The graph cycle count, ``edges - vertices + 1``.
        """
        edges = 0
        for y in range(self._height):
            for x in range(self._width):
                if (x, y) in self._pattern_cells:
                    continue
                for direction in (Direction.EAST, Direction.SOUTH):
                    dx, dy = DELTA[direction]
                    nx, ny = x + dx, y + dy
                    if (nx, ny) not in normal_cells:
                        continue
                    if not self._grid[y][x] & (1 << direction):
                        edges += 1
        return edges - len(normal_cells) + 1

    def _validate_pacman_spawn_cells(self) -> None:
        """Ensure Pac-Man's four corners and centre are usable corridors."""
        corners = (
            (0, 0),
            (self._width - 1, 0),
            (0, self._height - 1),
            (self._width - 1, self._height - 1),
        )
        if any(
            cell in self._pattern_cells or not self._open_neighbours(cell)
            for cell in corners
        ):
            raise ValueError("Pac-Man corners must be open corridors.")

        row_mid = {self._height // 2}
        col_mid = {self._width // 2}
        if self._height % 2 == 0:
            row_mid.add(self._height // 2 - 1)
        if self._width % 2 == 0:
            col_mid.add(self._width // 2 - 1)
        centres = {(x, y) for x in col_mid for y in row_mid}
        if not any(
            cell not in self._pattern_cells and self._open_neighbours(cell)
            for cell in centres
        ):
            raise ValueError("Pac-Man centre must be an open corridor.")

    def _contains_open_3x3_area(self) -> bool:
        """Return whether every internal wall of a 3x3 block is open."""
        for y in range(self._height - 2):
            for x in range(self._width - 2):
                horizontal_open = all(
                    not (
                        self._grid[row][col] & (1 << Direction.EAST)
                        or self._grid[row][col + 1]
                        & (1 << Direction.WEST)
                    )
                    for row in range(y, y + 3)
                    for col in range(x, x + 2)
                )
                vertical_open = all(
                    not (
                        self._grid[row][col] & (1 << Direction.SOUTH)
                        or self._grid[row + 1][col]
                        & (1 << Direction.NORTH)
                    )
                    for row in range(y, y + 2)
                    for col in range(x, x + 3)
                )
                if horizontal_open and vertical_open:
                    return True
        return False

    def save_to_file(self, filename: str) -> None:
        """Save maze in hex format with footer.

        Args:
            filename: Output filename.
        """
        # The footer is calculated from the final grid, not from the carving
        # history.  This keeps the serialized solution correct after braiding.
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
        return solve_bfs_path(
            self._grid, self._width, self._height, self._entry, self._exit
        )

    def get_pattern_cells(self) -> set[tuple[int, int]]:
        """Return the set of '42' pattern cell coordinates.

        Returns:
            Set of (x, y) tuples.
        """
        return self._pattern_cells.copy()

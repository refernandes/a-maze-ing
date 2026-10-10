"""Reusable maze generator used by both the CLI and future projects.

The public class deliberately owns the complete generation pipeline:

1. create a grid made only of closed cells;
2. reserve the isolated cells that draw ``42``;
3. carve a spanning tree with the selected algorithm;
4. optionally braid the tree for Pac-Man mode;
5. validate every rule before exposing or saving the result.

Keeping this orchestration in one class is important for the reusable
``mazegen`` package: a later project can use the same validated structure
without importing the command-line parser or the visualizer.
"""
from __future__ import annotations

from collections import deque
import random
from typing import Callable

from mazegen.algorithms import generate_dfs, generate_kruskal, generate_prim
from mazegen.pattern42 import compute_pattern_cells, stamp_pattern_42
from mazegen.solver import find_shortest_path, solve_bfs
from mazegen.types import ALL_WALLS, DELTA, OPPOSITE, Algorithm, Direction

StepCallback = Callable[[list[list[int]], tuple[int, int]], None]


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
        if entry == exit_pos:
            raise ValueError("Entry and exit must be different cells.")
        if not (0 <= entry[0] < width and 0 <= entry[1] < height):
            raise ValueError("Entry must be within bounds.")
        if not (0 <= exit_pos[0] < width and 0 <= exit_pos[1] < height):
            raise ValueError("Exit must be within bounds.")

        # The parser normally gives us an Algorithm enum.  Converting here as
        # well makes the reusable API friendly to callers that pass "DFS".
        try:
            algorithm = Algorithm(algorithm)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Unsupported algorithm: {algorithm}") from exc

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

    def generate(
        self,
        step_callback: StepCallback | None = None,
    ) -> None:
        """Generate and validate a maze with optional animation callbacks.

        Every call starts from a new all-walls grid.  The local random
        generator is intentionally kept as object state, so pressing ``R``
        creates a different maze while constructing two generators with the
        same seed remains reproducible.
        """
        self._reset_grid()
        self._place_pattern_42()
        self._check_entry_and_exit()
        self._carve_maze(step_callback)

        if not self._perfect:
            self._braid()
            self._ensure_pacman_layout()

        # Entry and exit are cells, not holes in the outside frame.  Closing
        # all four borders matches the subject and makes the graph model
        # identical to the file representation.
        self._validate_borders()
        self._validate_generated_maze()

    def _reset_grid(self) -> None:
        """Start a fresh maze with every wall closed."""
        self._grid = [
            [ALL_WALLS] * self._width for _ in range(self._height)
        ]

    def _place_pattern_42(self) -> None:
        """Reserve isolated cells used to draw the 42 pattern."""
        self._pattern_cells = compute_pattern_cells(
            self._width, self._height,
        )
        stamp_pattern_42(self._grid, self._pattern_cells)

    def _check_entry_and_exit(self) -> None:
        """Reject endpoints that overlap the isolated pattern."""
        if self._entry in self._pattern_cells:
            raise ValueError("Entry cannot overlap the '42' pattern.")
        if self._exit in self._pattern_cells:
            raise ValueError("Exit cannot overlap the '42' pattern.")

    def _carve_maze(self, step_callback: StepCallback | None) -> None:
        """Run the selected algorithm to open passages in the grid."""
        start_x, start_y = self._entry
        if self._algorithm == Algorithm.DFS:
            generate_dfs(
                self._grid,
                self._width,
                self._height,
                start_x,
                start_y,
                self._pattern_cells,
                self._rng,
                step_callback=step_callback,
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
                step_callback=step_callback,
            )
        else:
            generate_kruskal(
                self._grid,
                self._width,
                self._height,
                self._pattern_cells,
                self._rng,
                step_callback=step_callback,
            )

    def _braid(self) -> None:
        """Open extra passages until no more safe dead-ends can be removed."""
        previous_dead_end_count = -1
        while True:
            dead_ends = self._find_dead_ends()
            if not dead_ends:
                break
            if len(dead_ends) == previous_dead_end_count:
                break
            previous_dead_end_count = len(dead_ends)

            for dead_end in dead_ends:
                self._open_random_safe_passage(dead_end)

    def _find_dead_ends(self) -> list[tuple[int, int]]:
        """Return corridor cells that have exactly one open passage."""
        dead_ends: list[tuple[int, int]] = []
        for row in range(self._height):
            for column in range(self._width):
                position = (column, row)
                if position in self._pattern_cells:
                    continue
                if len(self._open_neighbors(position)) == 1:
                    dead_ends.append(position)
        return dead_ends

    def _open_random_safe_passage(
        self,
        cell: tuple[int, int],
    ) -> None:
        """Try random closed walls until one can open without a 3x3 area."""
        if len(self._open_neighbors(cell)) != 1:
            return

        candidates = self._closed_directions(cell)
        self._rng.shuffle(candidates)
        x, y = cell
        for direction in candidates:
            if self._try_open_edge(x, y, direction):
                return

    def _closed_directions(
        self,
        cell: tuple[int, int],
    ) -> list[Direction]:
        """List closed walls that lead to a normal cell inside the grid."""
        x, y = cell
        candidates: list[Direction] = []
        for direction in Direction:
            if not self._grid[y][x] & (1 << direction):
                continue

            dx, dy = DELTA[direction]
            neighbour = (x + dx, y + dy)
            if not self._is_inside(neighbour):
                continue
            if neighbour in self._pattern_cells:
                continue
            candidates.append(direction)
        return candidates

    def _is_inside(self, cell: tuple[int, int]) -> bool:
        """Return whether a coordinate belongs to the grid."""
        x, y = cell
        return 0 <= x < self._width and 0 <= y < self._height

    def _ensure_pacman_layout(self) -> None:
        """Ensure corners and center are open corridors."""
        required_cells = [
            (0, 0),
            (self._width - 1, 0),
            (0, self._height - 1),
            (self._width - 1, self._height - 1),
        ]
        required_cells.append((self._width // 2, self._height // 2))

        for cell in required_cells:
            self._give_cell_an_open_passage(cell)

    def _give_cell_an_open_passage(self, cell: tuple[int, int]) -> None:
        """Open one safe wall when a required spawn cell is too enclosed."""
        if not self._is_inside(cell) or cell in self._pattern_cells:
            return
        if len(self._open_neighbors(cell)) > 2:
            return

        candidates = self._closed_directions(cell)
        self._rng.shuffle(candidates)
        x, y = cell
        for direction in candidates:
            if self._try_open_edge(x, y, direction):
                return

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

    def _open_neighbors(self, cell: tuple[int, int]) -> list[tuple[int, int]]:
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
        """Check connectivity, walls, game mode, and corridor size."""
        normal_cells = self._validate_connectivity()
        self._validate_wall_coherence()
        self._validate_closed_borders()
        self._validate_loop_count(normal_cells)

        if not self._perfect:
            self._validate_pacman_spawn_cells()

        if self._contains_open_3x3_area():
            raise ValueError("Generated maze contains an open 3x3 area.")

    def _normal_cells(self) -> set[tuple[int, int]]:
        """Return every grid coordinate outside the isolated 42 pattern."""
        return {
            (x, y)
            for y in range(self._height)
            for x in range(self._width)
            if (x, y) not in self._pattern_cells
        }

    def _validate_connectivity(self) -> set[tuple[int, int]]:
        """Ensure every normal cell can be reached from the entry."""
        normal_cells = self._normal_cells()
        reachable = {self._entry}
        queue: deque[tuple[int, int]] = deque([self._entry])
        while queue:
            cell = queue.popleft()
            for neighbor in self._open_neighbors(cell):
                if neighbor in reachable:
                    continue
                reachable.add(neighbor)
                queue.append(neighbor)

        if reachable != normal_cells:
            missing = len(normal_cells - reachable)
            raise ValueError(
                f"Generated maze is disconnected ({missing} cell(s) "
                "cannot be reached from the entry)."
            )
        if self._exit not in reachable:
            raise ValueError("Generated maze has no path to the exit.")
        return normal_cells

    def _validate_wall_coherence(self) -> None:
        """Ensure every internal wall agrees on both neighbouring cells."""
        for row in range(self._height):
            for column in range(self._width):
                cell_walls = self._grid[row][column]
                if column + 1 < self._width:
                    east_wall = bool(cell_walls & (1 << Direction.EAST))
                    west_wall = bool(
                        self._grid[row][column + 1]
                        & (1 << Direction.WEST)
                    )
                    if east_wall != west_wall:
                        raise ValueError(
                            "Generated maze has incoherent walls."
                        )
                if row + 1 < self._height:
                    south_wall = bool(cell_walls & (1 << Direction.SOUTH))
                    north_wall = bool(
                        self._grid[row + 1][column]
                        & (1 << Direction.NORTH)
                    )
                    if south_wall != north_wall:
                        raise ValueError(
                            "Generated maze has incoherent walls."
                        )

    def _validate_closed_borders(self) -> None:
        """Ensure the outside edge of the maze has no openings."""
        for column in range(self._width):
            if not self._grid[0][column] & (1 << Direction.NORTH):
                raise ValueError("Generated maze has an open north border.")
            if not self._grid[self._height - 1][column] & (
                1 << Direction.SOUTH
            ):
                raise ValueError("Generated maze has an open south border.")
        for row in range(self._height):
            if not self._grid[row][0] & (1 << Direction.WEST):
                raise ValueError("Generated maze has an open west border.")
            if not self._grid[row][self._width - 1] & (
                1 << Direction.EAST
            ):
                raise ValueError("Generated maze has an open east border.")

    def _validate_loop_count(
        self,
        normal_cells: set[tuple[int, int]],
    ) -> None:
        """Check the number of independent routes for the selected mode."""
        # For a connected graph, E - V + 1 is the number of independent loops.
        # A spanning tree must have zero; Pac-Man mode needs at least two.
        edges = 0
        for row in range(self._height):
            for column in range(self._width):
                if (column, row) not in normal_cells:
                    continue
                for direction in (Direction.EAST, Direction.SOUTH):
                    dx, dy = DELTA[direction]
                    neighbor = (column + dx, row + dy)
                    if neighbor not in normal_cells:
                        continue
                    if not self._grid[row][column] & (1 << direction):
                        edges += 1
        loops = edges - len(normal_cells) + 1
        if self._perfect and loops != 0:
            raise ValueError("PERFECT=True requires a maze without loops.")
        if not self._perfect and loops < 2:
            raise ValueError(
                "Pac-Man mode needs at least two independent routes; "
                "the requested dimensions are too small."
            )

    def _validate_pacman_spawn_cells(self) -> None:
        """Ensure Pac-Man's four corners and centre are usable corridors."""
        corners = (
            (0, 0),
            (self._width - 1, 0),
            (0, self._height - 1),
            (self._width - 1, self._height - 1),
        )
        if any(
            cell in self._pattern_cells or not self._open_neighbors(cell)
            for cell in corners
        ):
            raise ValueError("Pac-Man corners must be open corridors.")

        middle_rows = {self._height // 2}
        middle_columns = {self._width // 2}
        if self._height % 2 == 0:
            middle_rows.add(self._height // 2 - 1)
        if self._width % 2 == 0:
            middle_columns.add(self._width // 2 - 1)
        center_cells = {
            (column, row)
            for column in middle_columns
            for row in middle_rows
        }
        if not any(
            cell not in self._pattern_cells and self._open_neighbors(cell)
            for cell in center_cells
        ):
            raise ValueError("Pac-Man centre must be an open corridor.")

    def _contains_open_3x3_area(self) -> bool:
        """Return whether any 3x3 block has no internal walls."""
        for top_row in range(self._height - 2):
            for left_column in range(self._width - 2):
                if (
                    self._horizontal_passages_are_open(
                        top_row, left_column
                    )
                    and self._vertical_passages_are_open(
                        top_row, left_column
                    )
                ):
                    return True
        return False

    def _horizontal_passages_are_open(
        self,
        top_row: int,
        left_column: int,
    ) -> bool:
        """Check the six left-to-right passages inside one 3x3 block."""
        for row in range(top_row, top_row + 3):
            for column in range(left_column, left_column + 2):
                if not self._passage_is_open(row, column, Direction.EAST):
                    return False
        return True

    def _vertical_passages_are_open(
        self,
        top_row: int,
        left_column: int,
    ) -> bool:
        """Check the six top-to-bottom passages inside one 3x3 block."""
        for row in range(top_row, top_row + 2):
            for column in range(left_column, left_column + 3):
                if not self._passage_is_open(row, column, Direction.SOUTH):
                    return False
        return True

    def _passage_is_open(
        self,
        row: int,
        column: int,
        direction: Direction,
    ) -> bool:
        """Check that both cells agree that a shared wall is open."""
        dx, dy = DELTA[direction]
        neighbor_row = row + dy
        neighbor_column = column + dx
        current_cell = self._grid[row][column]
        neighbor_cell = self._grid[neighbor_row][neighbor_column]
        current_wall_is_closed = current_cell & (1 << direction)
        neighbor_wall_is_closed = neighbor_cell & (
            1 << OPPOSITE[direction]
        )
        return not current_wall_is_closed and not neighbor_wall_is_closed

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
        return find_shortest_path(
            self._grid,
            self._width,
            self._height,
            self._entry,
            self._exit,
        )

    def get_pattern_cells(self) -> set[tuple[int, int]]:
        """Return the set of '42' pattern cell coordinates.

        Returns:
            Set of (x, y) tuples.
        """
        return self._pattern_cells.copy()

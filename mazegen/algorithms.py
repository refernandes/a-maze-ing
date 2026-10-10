"""Maze-carving algorithms.

Each algorithm opens passages between neighbouring cells.  The shared helper
updates both wall bits so the grid always has a consistent representation.
"""
from __future__ import annotations

import random
from typing import Callable

from mazegen.types import DELTA, OPPOSITE, Direction

Cell = tuple[int, int]
StepCallback = Callable[[list[list[int]], Cell], None]
FrontierEdge = tuple[Cell, Direction, Cell]


def _inside_grid(cell: Cell, width: int, height: int) -> bool:
    """Return whether a cell coordinate is inside the grid."""
    x, y = cell
    return 0 <= x < width and 0 <= y < height


def _unvisited_neighbors(
    cell: Cell,
    width: int,
    height: int,
    blocked_cells: set[Cell],
    visited_cells: set[Cell],
) -> list[tuple[Direction, Cell]]:
    """Find neighbouring cells that are open to visit."""
    x, y = cell
    neighbors: list[tuple[Direction, Cell]] = []
    for direction, (dx, dy) in DELTA.items():
        neighbor = (x + dx, y + dy)
        if not _inside_grid(neighbor, width, height):
            continue
        if neighbor in blocked_cells or neighbor in visited_cells:
            continue
        neighbors.append((direction, neighbor))
    return neighbors


def _open_passage(
    grid: list[list[int]],
    cell: Cell,
    direction: Direction,
    neighbor: Cell,
) -> None:
    """Open the shared wall in both cells."""
    x, y = cell
    neighbor_x, neighbor_y = neighbor
    grid[y][x] &= ~(1 << direction)
    grid[neighbor_y][neighbor_x] &= ~(1 << OPPOSITE[direction])


def _report_carved_cell(
    callback: StepCallback | None,
    grid: list[list[int]],
    cell: Cell,
) -> None:
    """Tell the renderer that one more cell has been connected."""
    if callback is not None:
        callback(grid, cell)


def generate_dfs(
    grid: list[list[int]],
    width: int,
    height: int,
    start_x: int,
    start_y: int,
    blocked: set[Cell],
    rng: random.Random,
    step_callback: StepCallback | None = None,
) -> None:
    """Carve a maze with depth-first search and backtracking.

    The algorithm keeps a stack of the current path.  It chooses a random
    unvisited neighbour, opens the wall, and backtracks when a cell has no
    unvisited neighbours.
    """
    start_cell = (start_x, start_y)
    if start_cell in blocked:
        return

    visited_cells = {start_cell}
    path_stack = [start_cell]

    while path_stack:
        current_cell = path_stack[-1]
        choices = _unvisited_neighbors(
            current_cell, width, height, blocked, visited_cells
        )
        if not choices:
            path_stack.pop()
            continue

        direction, next_cell = rng.choice(choices)
        _open_passage(grid, current_cell, direction, next_cell)
        visited_cells.add(next_cell)
        path_stack.append(next_cell)
        _report_carved_cell(step_callback, grid, next_cell)


def _add_frontier_edges(
    cell: Cell,
    frontier: list[FrontierEdge],
    width: int,
    height: int,
    blocked_cells: set[Cell],
    visited_cells: set[Cell],
) -> None:
    """Add edges from one visited cell to each unvisited neighbour."""
    for direction, neighbor in _unvisited_neighbors(
        cell, width, height, blocked_cells, visited_cells
    ):
        frontier.append((cell, direction, neighbor))


def generate_prim(
    grid: list[list[int]],
    width: int,
    height: int,
    start_x: int,
    start_y: int,
    blocked: set[Cell],
    rng: random.Random,
    step_callback: StepCallback | None = None,
) -> None:
    """Carve a maze by growing a random frontier from the start cell."""
    start_cell = (start_x, start_y)
    if start_cell in blocked:
        return

    visited_cells = {start_cell}
    frontier: list[FrontierEdge] = []
    _add_frontier_edges(
        start_cell, frontier, width, height, blocked, visited_cells
    )

    while frontier:
        edge_index = rng.randrange(len(frontier))
        current_cell, direction, next_cell = frontier.pop(edge_index)
        if next_cell in visited_cells:
            continue

        _open_passage(grid, current_cell, direction, next_cell)
        visited_cells.add(next_cell)
        _report_carved_cell(step_callback, grid, next_cell)
        _add_frontier_edges(
            next_cell, frontier, width, height, blocked, visited_cells
        )


class UnionFind:
    """Track which cells are already connected for Kruskal's algorithm."""

    def __init__(self, size: int) -> None:
        """Start with each cell in its own group."""
        self.parent: list[int] = list(range(size))
        self.rank: list[int] = [0] * size

    def find(self, item: int) -> int:
        """Return the group's representative, shortening the lookup path."""
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, first: int, second: int) -> bool:
        """Join two groups; return false if they were already connected."""
        first_root = self.find(first)
        second_root = self.find(second)
        if first_root == second_root:
            return False

        if self.rank[first_root] < self.rank[second_root]:
            first_root, second_root = second_root, first_root

        self.parent[second_root] = first_root
        if self.rank[first_root] == self.rank[second_root]:
            self.rank[first_root] += 1
        return True


def generate_kruskal(
    grid: list[list[int]],
    width: int,
    height: int,
    blocked: set[Cell],
    rng: random.Random,
    step_callback: StepCallback | None = None,
) -> None:
    """Carve a maze by choosing random edges that join separate groups."""
    groups = UnionFind(width * height)
    candidate_edges: list[FrontierEdge] = []

    # Store each possible edge once by checking only its east and south sides.
    for y in range(height):
        for x in range(width):
            cell = (x, y)
            if cell in blocked:
                continue
            for direction in (Direction.EAST, Direction.SOUTH):
                dx, dy = DELTA[direction]
                neighbor = (x + dx, y + dy)
                if _inside_grid(neighbor, width, height):
                    if neighbor not in blocked:
                        candidate_edges.append((cell, direction, neighbor))

    rng.shuffle(candidate_edges)

    for cell, direction, neighbor in candidate_edges:
        cell_id = cell[1] * width + cell[0]
        neighbor_id = neighbor[1] * width + neighbor[0]
        if not groups.union(cell_id, neighbor_id):
            continue

        _open_passage(grid, cell, direction, neighbor)
        _report_carved_cell(step_callback, grid, neighbor)

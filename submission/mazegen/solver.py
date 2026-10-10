"""Shortest-path solver used by the output footer and the visualizer.

Breadth-first search is the right choice because every movement between two
neighbouring cells has the same cost.  The first time BFS reaches the exit it
has therefore found a shortest path, not merely any path.
"""
from __future__ import annotations

from collections import deque

from mazegen.types import DELTA, DIRECTION_CHARS, OPPOSITE


def solve_bfs(
    grid: list[list[int]],
    width: int,
    height: int,
    start: tuple[int, int],
    end: tuple[int, int],
) -> str:
    """Return the shortest path as direction letters separated by commas.

    Args:
        grid: The maze grid.
        width: Grid width.
        height: Grid height.
        start: Starting coordinate (x, y).
        end: Ending coordinate (x, y).

    Returns:
        A string of directions separated by ', '.
    """
    path = find_shortest_path(grid, width, height, start, end)
    if not path:
        return ""

    direction_names = {
        movement: DIRECTION_CHARS[direction]
        for direction, movement in DELTA.items()
    }
    path_directions: list[str] = []
    for previous_cell, current_cell in zip(path, path[1:]):
        move = (
            current_cell[0] - previous_cell[0],
            current_cell[1] - previous_cell[1],
        )
        path_directions.append(direction_names[move])
    return ", ".join(path_directions)


def find_shortest_path(
    grid: list[list[int]],
    width: int,
    height: int,
    start: tuple[int, int],
    end: tuple[int, int],
) -> list[tuple[int, int]]:
    """Return the shortest route as a list of ``(x, y)`` cells."""
    if not _inside_grid(start, width, height):
        return []
    if not _inside_grid(end, width, height):
        return []

    queue: deque[tuple[int, int]] = deque([start])
    visited: set[tuple[int, int]] = {start}
    parent: dict[tuple[int, int], tuple[int, int]] = {}

    while queue:
        current_cell = queue.popleft()
        if current_cell == end:
            break

        column, row = current_cell
        current_walls = grid[row][column]
        for direction, (dx, dy) in DELTA.items():
            if current_walls & (1 << direction):
                continue

            neighbor = (column + dx, row + dy)
            if not _inside_grid(neighbor, width, height):
                continue

            # Both cells must agree that the shared wall is open.
            neighbor_x, neighbor_y = neighbor
            neighbor_walls = grid[neighbor_y][neighbor_x]
            if neighbor_walls & (1 << OPPOSITE[direction]):
                continue
            if neighbor in visited:
                continue

            visited.add(neighbor)
            parent[neighbor] = current_cell
            queue.append(neighbor)

    if end not in visited:
        return []

    path = [end]
    current_cell = end
    while current_cell != start:
        current_cell = parent[current_cell]
        path.append(current_cell)
    path.reverse()
    return path


def _inside_grid(
    cell: tuple[int, int],
    width: int,
    height: int,
) -> bool:
    """Return whether an ``(x, y)`` coordinate is inside the grid."""
    x, y = cell
    return 0 <= x < width and 0 <= y < height

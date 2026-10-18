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
    """Find the shortest path using BFS.

    Args:
        grid: The maze grid.
        width: Grid width.
        height: Grid height.
        start: Starting coordinate (x, y).
        end: Ending coordinate (x, y).

    Returns:
        A string of directions separated by ', '.
    """
    directions = solve_bfs_directions(grid, width, height, start, end)
    return ", ".join(directions)


def solve_bfs_path(
    grid: list[list[int]],
    width: int,
    height: int,
    start: tuple[int, int],
    end: tuple[int, int],
) -> list[tuple[int, int]]:
    """Return the shortest route as grid coordinates.

    Args:
        grid: Maze cells encoded as wall bit masks.
        width: Number of columns in the grid.
        height: Number of rows in the grid.
        start: Entry coordinate as ``(x, y)``.
        end: Exit coordinate as ``(x, y)``.

    Returns:
        Coordinates from entry through exit, or an empty list if unreachable.
    """
    if not (0 <= start[0] < width and 0 <= start[1] < height):
        return []
    if not (0 <= end[0] < width and 0 <= end[1] < height):
        return []

    queue: deque[tuple[int, int]] = deque([start])
    visited: set[tuple[int, int]] = {start}
    parent: dict[tuple[int, int], tuple[int, int]] = {}

    while queue:
        cx, cy = queue.popleft()
        if (cx, cy) == end:
            break

        cell_val = grid[cy][cx]
        for d, (dx, dy) in DELTA.items():
            if not (cell_val & (1 << d)):
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < width and 0 <= ny < height:
                    # A passage is valid only when both cells agree.  This
                    # mirrors the generator's validation and protects the
                    # reusable solver from malformed caller-provided grids.
                    if grid[ny][nx] & (1 << OPPOSITE[d]):
                        continue
                    if (nx, ny) not in visited:
                        visited.add((nx, ny))
                        parent[(nx, ny)] = (cx, cy)
                        queue.append((nx, ny))

    if end not in visited:
        return []

    path: list[tuple[int, int]] = []
    curr = end
    while curr != start:
        path.append(curr)
        curr = parent[curr]

    path.append(start)
    path.reverse()
    return path


def solve_bfs_directions(
    grid: list[list[int]],
    width: int,
    height: int,
    start: tuple[int, int],
    end: tuple[int, int],
) -> list[str]:
    """Return the shortest route as compass direction letters.

    Args:
        grid: Maze cells encoded as wall bit masks.
        width: Number of columns in the grid.
        height: Number of rows in the grid.
        start: Entry coordinate as ``(x, y)``.
        end: Exit coordinate as ``(x, y)``.

    Returns:
        Direction letters from entry to exit, or an empty list if unreachable.
    """
    path = solve_bfs_path(grid, width, height, start, end)
    directions: list[str] = []
    for current, following in zip(path, path[1:]):
        dx = following[0] - current[0]
        dy = following[1] - current[1]
        for direction, (step_x, step_y) in DELTA.items():
            if (dx, dy) == (step_x, step_y):
                directions.append(DIRECTION_CHARS[direction])
                break
    return directions

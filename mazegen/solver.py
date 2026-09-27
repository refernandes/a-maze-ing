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
    if not (0 <= start[0] < width and 0 <= start[1] < height):
        return ""
    if not (0 <= end[0] < width and 0 <= end[1] < height):
        return ""

    queue: deque[tuple[int, int]] = deque([start])
    visited: set[tuple[int, int]] = {start}
    parent: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}

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
                        parent[(nx, ny)] = ((cx, cy), DIRECTION_CHARS[d])
                        queue.append((nx, ny))

    if end not in visited:
        return ""

    path_dirs: list[str] = []
    curr = end
    while curr != start:
        prev, direction_char = parent[curr]
        path_dirs.append(direction_char)
        curr = prev

    path_dirs.reverse()
    return ", ".join(path_dirs)

"""Shortest-path search and output path formatting."""
from __future__ import annotations

from collections import deque

from mazegen.constants import LETTER, MOVE, OPPOSITE


def shortest_path(
    grid: list[list[int]],
    width: int,
    height: int,
    start: tuple[int, int],
    end: tuple[int, int],
) -> list[tuple[int, int]]:
    """Return the shortest sequence of cells from start to end using BFS."""
    parents: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        if current == end:
            break
        x, y = current
        for wall, (dx, dy) in MOVE.items():
            neighbour = (x + dx, y + dy)
            if not (
                0 <= neighbour[0] < width
                and 0 <= neighbour[1] < height
            ):
                continue
            neighbour_walls = grid[neighbour[1]][neighbour[0]]
            if grid[y][x] & wall or neighbour_walls & OPPOSITE[wall]:
                continue
            if neighbour not in parents:
                parents[neighbour] = current
                queue.append(neighbour)

    if end not in parents:
        return []
    path: list[tuple[int, int]] = []
    cursor: tuple[int, int] | None = end
    while cursor is not None:
        path.append(cursor)
        cursor = parents[cursor]
    return list(reversed(path))


def path_directions(path: list[tuple[int, int]]) -> str:
    """Convert a cell path to the subject's comma-separated directions."""
    directions = []
    for start, end in zip(path, path[1:]):
        move = (end[0] - start[0], end[1] - start[1])
        wall = next(bit for bit, delta in MOVE.items() if delta == move)
        directions.append(LETTER[wall])
    return ", ".join(directions)

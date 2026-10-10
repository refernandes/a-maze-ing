"""Maze carving algorithms."""
from __future__ import annotations

import random

from mazegen.constants import MOVE, OPPOSITE


def carve_depth_first(
    grid: list[list[int]],
    width: int,
    height: int,
    entry: tuple[int, int],
    blocked: set[tuple[int, int]],
    rng: random.Random,
) -> set[tuple[int, int]]:
    """Carve one randomized spanning tree with iterative DFS."""
    visited = {entry}
    stack = [entry]
    while stack:
        x, y = stack[-1]
        choices = []
        for wall, (dx, dy) in MOVE.items():
            neighbour = (x + dx, y + dy)
            if (0 <= neighbour[0] < width and 0 <= neighbour[1] < height
                    and neighbour not in visited and neighbour not in blocked):
                choices.append((wall, neighbour))
        if not choices:
            stack.pop()
            continue

        wall, neighbour = rng.choice(choices)
        nx, ny = neighbour
        grid[y][x] &= ~wall
        grid[ny][nx] &= ~OPPOSITE[wall]
        visited.add(neighbour)
        stack.append(neighbour)
    return visited

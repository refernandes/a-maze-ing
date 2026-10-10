"""Pac-Man board braiding and spawn-cell preparation."""
from __future__ import annotations

import random

from mazegen.rules import (
    centre_cells,
    open_neighbours,
    safe_closed_walls,
    try_open_without_3x3,
)


def remove_dead_ends(
    grid: list[list[int]],
    width: int,
    height: int,
    pattern: set[tuple[int, int]],
    rng: random.Random,
) -> None:
    """Add safe passages to dead ends until no more changes are possible."""
    while True:
        before = tuple(tuple(row) for row in grid)
        for y in range(height):
            for x in range(width):
                if ((x, y) in pattern
                        or open_neighbours(grid, width, height, x, y) != 1):
                    continue
                choices = safe_closed_walls(
                    grid, width, height, pattern, x, y
                )
                rng.shuffle(choices)
                for wall in choices:
                    if try_open_without_3x3(
                        grid, width, height, x, y, wall
                    ):
                        break
        if tuple(tuple(row) for row in grid) == before:
            return


def open_spawn_cells(
    grid: list[list[int]],
    width: int,
    height: int,
    pattern: set[tuple[int, int]],
    rng: random.Random,
) -> None:
    """Open the four corners and at least one cell at the board centre."""
    corners = (
        (0, 0), (width - 1, 0),
        (0, height - 1), (width - 1, height - 1),
    )
    for x, y in corners:
        _open_corridor(grid, width, height, pattern, rng, x, y)

    centres = centre_cells(width, height)
    if not any(
        open_neighbours(grid, width, height, x, y)
        for x, y in centres if (x, y) not in pattern
    ):
        for x, y in centres:
            if (x, y) not in pattern:
                _open_corridor(grid, width, height, pattern, rng, x, y)
                if open_neighbours(grid, width, height, x, y):
                    break


def _open_corridor(
    grid: list[list[int]],
    width: int,
    height: int,
    pattern: set[tuple[int, int]],
    rng: random.Random,
    x: int,
    y: int,
) -> None:
    """Open one safe neighbouring wall when the requested spawn is isolated."""
    if (x, y) in pattern or open_neighbours(grid, width, height, x, y):
        return
    choices = safe_closed_walls(grid, width, height, pattern, x, y)
    rng.shuffle(choices)
    for wall in choices:
        if try_open_without_3x3(grid, width, height, x, y, wall):
            break

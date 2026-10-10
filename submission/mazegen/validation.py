"""Validation of maze connectivity, geometry and generation mode."""
from __future__ import annotations

from mazegen.constants import EAST, MOVE, NORTH, SOUTH, WEST
from mazegen.rules import (
    can_move,
    centre_cells,
    has_open_3x3,
    open_neighbours,
)


def validate_maze(
    grid: list[list[int]],
    width: int,
    height: int,
    entry: tuple[int, int],
    perfect: bool,
    pattern: set[tuple[int, int]],
) -> None:
    """Raise ``ValueError`` when a generated maze violates the subject."""
    playable = {
        (x, y)
        for y in range(height)
        for x in range(width)
        if (x, y) not in pattern
    }
    reached = {entry}
    stack = [entry]
    while stack:
        x, y = stack.pop()
        for wall, (dx, dy) in MOVE.items():
            neighbour = (x + dx, y + dy)
            if (can_move(grid, width, height, x, y, wall)
                    and neighbour not in reached):
                reached.add(neighbour)
                stack.append(neighbour)
    if reached != playable:
        raise ValueError("Generated maze contains unreachable corridors.")

    edges, dead_ends = _count_edges_and_dead_ends(
        grid, width, height, pattern
    )
    _validate_wall_coherence(grid, width, height)
    _validate_borders(grid, width, height)
    if has_open_3x3(grid, width, height):
        raise ValueError("The maze cannot contain an open 3 by 3 area.")

    loops = edges - len(playable) + 1
    if perfect and loops != 0:
        raise ValueError("PERFECT=True requires a maze with no loops.")
    if not perfect:
        if loops < 2:
            raise ValueError("Pac-Man mode requires at least two loops.")
        if dead_ends > 2:
            raise ValueError("Pac-Man mode has too many dead ends.")
        _validate_pacman_spawns(
            grid, width, height, pattern
        )


def _count_edges_and_dead_ends(
    grid: list[list[int]],
    width: int,
    height: int,
    pattern: set[tuple[int, int]],
) -> tuple[int, int]:
    """Count open graph edges and dead ends among playable cells."""
    edges = 0
    dead_ends = 0
    for y in range(height):
        for x in range(width):
            if (x, y) in pattern:
                continue
            if x + 1 < width and not grid[y][x] & EAST:
                edges += 1
            if y + 1 < height and not grid[y][x] & SOUTH:
                edges += 1
            if open_neighbours(grid, width, height, x, y) == 1:
                dead_ends += 1
    return edges, dead_ends


def _validate_wall_coherence(
    grid: list[list[int]], width: int, height: int
) -> None:
    """Require each pair of cells to agree about their shared wall."""
    for y in range(height):
        for x in range(width):
            if x + 1 < width:
                if bool(grid[y][x] & EAST) != bool(grid[y][x + 1] & WEST):
                    raise ValueError("Neighbouring walls do not match.")
            if y + 1 < height:
                if bool(grid[y][x] & SOUTH) != bool(grid[y + 1][x] & NORTH):
                    raise ValueError("Neighbouring walls do not match.")
            if not 0 <= grid[y][x] <= 15:
                raise ValueError(
                    "Cell wall values must be hexadecimal digits."
                )


def _validate_borders(
    grid: list[list[int]], width: int, height: int
) -> None:
    """Require all walls facing outside the grid to stay closed."""
    for x in range(width):
        if not grid[0][x] & NORTH or not grid[-1][x] & SOUTH:
            raise ValueError("The external border must stay closed.")
    for y in range(height):
        if not grid[y][0] & WEST or not grid[y][-1] & EAST:
            raise ValueError("The external border must stay closed.")


def _validate_pacman_spawns(
    grid: list[list[int]],
    width: int,
    height: int,
    pattern: set[tuple[int, int]],
) -> None:
    """Require open corners and a playable central cell."""
    corners = (
        (0, 0), (width - 1, 0),
        (0, height - 1), (width - 1, height - 1),
    )
    if any(not open_neighbours(grid, width, height, x, y)
           for x, y in corners):
        raise ValueError("Pac-Man corners must be open corridors.")
    if not any(
        (x, y) not in pattern and open_neighbours(grid, width, height, x, y)
        for x, y in centre_cells(width, height)
    ):
        raise ValueError("Pac-Man centre must be an open corridor.")

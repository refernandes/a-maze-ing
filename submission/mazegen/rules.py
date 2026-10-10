"""Shared checks and safe passage operations for maze grids."""
from __future__ import annotations

from mazegen.constants import EAST, MOVE, NORTH, OPPOSITE, SOUTH, WALLS, WEST


def inside(width: int, height: int, point: tuple[int, int]) -> bool:
    """Return whether a cell coordinate is inside the grid."""
    return 0 <= point[0] < width and 0 <= point[1] < height


def can_move(
    grid: list[list[int]],
    width: int,
    height: int,
    x: int,
    y: int,
    wall: int,
) -> bool:
    """Check that both sides of a neighbouring passage are open."""
    dx, dy = MOVE[wall]
    nx, ny = x + dx, y + dy
    return (
        inside(width, height, (nx, ny))
        and not grid[y][x] & wall
        and not grid[ny][nx] & OPPOSITE[wall]
    )


def open_neighbours(
    grid: list[list[int]], width: int, height: int, x: int, y: int
) -> int:
    """Count open passages to valid neighbours of one cell."""
    return sum(
        can_move(grid, width, height, x, y, wall) for wall in WALLS
    )


def centre_cells(width: int, height: int) -> list[tuple[int, int]]:
    """Return one central cell or the central 2 by 2 on even dimensions."""
    xs = {width // 2}
    ys = {height // 2}
    if width % 2 == 0:
        xs.add(width // 2 - 1)
    if height % 2 == 0:
        ys.add(height // 2 - 1)
    return [(x, y) for y in ys for x in xs]


def safe_closed_walls(
    grid: list[list[int]],
    width: int,
    height: int,
    pattern: set[tuple[int, int]],
    x: int,
    y: int,
) -> list[int]:
    """Find closed walls leading to cells outside and around the 42 stamp."""
    choices = []
    for wall in WALLS:
        dx, dy = MOVE[wall]
        neighbour = (x + dx, y + dy)
        if (grid[y][x] & wall and inside(width, height, neighbour)
                and neighbour not in pattern):
            choices.append(wall)
    return choices


def try_open_without_3x3(
    grid: list[list[int]],
    width: int,
    height: int,
    x: int,
    y: int,
    wall: int,
) -> bool:
    """Open a passage unless it creates a fully open 3 by 3 block."""
    dx, dy = MOVE[wall]
    nx, ny = x + dx, y + dy
    old_here, old_there = grid[y][x], grid[ny][nx]
    grid[y][x] &= ~wall
    grid[ny][nx] &= ~OPPOSITE[wall]
    if has_open_3x3_near(grid, width, height, (x, y), (nx, ny)):
        grid[y][x], grid[ny][nx] = old_here, old_there
        return False
    return True


def has_open_3x3(grid: list[list[int]], width: int, height: int) -> bool:
    """Return whether any 3 by 3 block has every internal wall open."""
    return any(
        is_open_3x3(grid, x, y)
        for y in range(height - 2)
        for x in range(width - 2)
    )


def has_open_3x3_near(
    grid: list[list[int]],
    width: int,
    height: int,
    first: tuple[int, int],
    second: tuple[int, int],
) -> bool:
    """Check blocks containing either endpoint of a newly opened edge."""
    candidates = set()
    for x, y in (first, second):
        for top in range(max(0, y - 2), min(y, height - 3) + 1):
            for left in range(max(0, x - 2), min(x, width - 3) + 1):
                candidates.add((left, top))
    return any(is_open_3x3(grid, x, y) for x, y in candidates)


def is_open_3x3(grid: list[list[int]], left: int, top: int) -> bool:
    """Check whether one 3 by 3 block has all its internal walls open."""
    horizontal = all(
        not grid[row][col] & EAST and not grid[row][col + 1] & WEST
        for row in range(top, top + 3)
        for col in range(left, left + 2)
    )
    vertical = all(
        not grid[row][col] & SOUTH and not grid[row + 1][col] & NORTH
        for row in range(top, top + 2)
        for col in range(left, left + 3)
    )
    return horizontal and vertical

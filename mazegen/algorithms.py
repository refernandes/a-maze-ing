"""Depth-first maze generation."""
from __future__ import annotations

import random

from mazegen.types import DELTA, OPPOSITE, Direction


def generate_dfs(
    grid: list[list[int]],
    width: int,
    height: int,
    start_x: int,
    start_y: int,
    blocked: set[tuple[int, int]],
    rng: random.Random,
) -> None:
    """Generate a maze with iterative depth-first search.

    Args:
        grid: The maze grid to modify.
        width: Grid width.
        height: Grid height.
        start_x: Starting x coordinate.
        start_y: Starting y coordinate.
        blocked: Coordinates that cannot be visited.
        rng: Random instance used to choose each next cell.
    """
    if (start_x, start_y) in blocked:
        return

    visited: set[tuple[int, int]] = {(start_x, start_y)}
    stack: list[tuple[int, int]] = [(start_x, start_y)]

    while stack:
        x, y = stack[-1]
        neighbors: list[tuple[Direction, int, int]] = []

        for direction, (dx, dy) in DELTA.items():
            nx, ny = x + dx, y + dy
            if (
                0 <= nx < width
                and 0 <= ny < height
                and (nx, ny) not in blocked
                and (nx, ny) not in visited
            ):
                neighbors.append((direction, nx, ny))

        if not neighbors:
            stack.pop()
            continue

        direction, nx, ny = rng.choice(neighbors)
        grid[y][x] &= ~(1 << direction)
        grid[ny][nx] &= ~(1 << OPPOSITE[direction])
        visited.add((nx, ny))
        stack.append((nx, ny))

    # The 42 pattern can split the grid into separate regions. Connect each
    # remaining walkable region to the cells already visited.
    for y in range(height):
        for x in range(width):
            if (x, y) in blocked or (x, y) in visited:
                continue

            for direction, (dx, dy) in DELTA.items():
                nx, ny = x + dx, y + dy
                if (
                    0 <= nx < width
                    and 0 <= ny < height
                    and (nx, ny) in visited
                ):
                    grid[y][x] &= ~(1 << direction)
                    grid[ny][nx] &= ~(1 << OPPOSITE[direction])
                    visited.add((x, y))
                    stack.append((x, y))
                    break

            while stack:
                cx, cy = stack[-1]
                next_cells: list[tuple[Direction, int, int]] = []
                for direction, (dx, dy) in DELTA.items():
                    nx, ny = cx + dx, cy + dy
                    if (
                        0 <= nx < width
                        and 0 <= ny < height
                        and (nx, ny) not in blocked
                        and (nx, ny) not in visited
                    ):
                        next_cells.append((direction, nx, ny))

                if not next_cells:
                    stack.pop()
                    continue

                direction, nx, ny = rng.choice(next_cells)
                grid[cy][cx] &= ~(1 << direction)
                grid[ny][nx] &= ~(1 << OPPOSITE[direction])
                visited.add((nx, ny))
                stack.append((nx, ny))

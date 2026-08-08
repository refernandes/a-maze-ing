"""Pattern 42 logic for A-Maze-ing."""
from __future__ import annotations

import sys


def get_pattern_42() -> list[list[int]]:
    """Return a 2D bitmap of the '42' pattern.

    Returns:
        A list of rows where 1 means cell should be isolated.
    """
    pattern_str: list[str] = [
        "#... .###",
        "#... ...#",
        "#..# .###",
        "#### .#..",
        "...# .#..",
        "...# .###",
    ]
    bitmap: list[list[int]] = []
    for row in pattern_str:
        mapped_row: list[int] = []
        for char in row:
            if char == "#":
                mapped_row.append(1)
            else:
                mapped_row.append(0)
        bitmap.append(mapped_row)
    return bitmap


def compute_pattern_cells(
    grid_width: int,
    grid_height: int,
) -> set[tuple[int, int]]:
    """Compute the (x,y) positions for the '42' pattern centered in the grid.

    Args:
        grid_width: Grid width.
        grid_height: Grid height.

    Returns:
        Set of coordinates that are part of the '42' pattern.
    """
    pattern = get_pattern_42()
    p_height = len(pattern)
    if p_height == 0:
        return set()
    p_width = len(pattern[0])

    margin = 2
    if (
        grid_width < p_width + 2 * margin
        or grid_height < p_height + 2 * margin
    ):
        print(
            "Warning: Grid too small to fit '42' pattern with margin.",
            file=sys.stderr,
        )
        return set()

    start_x = (grid_width - p_width) // 2
    start_y = (grid_height - p_height) // 2

    cells: set[tuple[int, int]] = set()
    for py in range(p_height):
        for px in range(p_width):
            if pattern[py][px] == 1:
                cells.add((start_x + px, start_y + py))
    return cells


def stamp_pattern_42(
    grid: list[list[int]],
    pattern_cells: set[tuple[int, int]],
) -> None:
    """Set all pattern cells to 15 (all walls closed, fully isolated).

    Args:
        grid: The maze grid to modify.
        pattern_cells: Set of pattern cell coordinates.
    """
    for x, y in pattern_cells:
        grid[y][x] = 15

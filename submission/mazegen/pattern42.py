"""Construction of the isolated cells that visibly draw ``42``.

The subject allows the pattern to be omitted for a grid that is too small.
The generator therefore returns an empty set in that case, but announces the
decision explicitly so the person running the program understands why the
output has no stamp.
"""
from __future__ import annotations

import sys


def get_pattern_42() -> list[list[int]]:
    """Return a 2D bitmap of the '42' pattern.

    Returns:
        A list of rows where 1 means cell should be isolated.
    """
    pattern_rows: list[str] = [
        "#... .###",
        "#... ...#",
        "#..# .###",
        "#### .#..",
        "...# .#..",
        "...# .###",
    ]
    bitmap: list[list[int]] = []
    for pattern_row in pattern_rows:
        bitmap_row: list[int] = []
        for symbol in pattern_row:
            bitmap_row.append(1 if symbol == "#" else 0)
        bitmap.append(bitmap_row)
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
    pattern_height = len(pattern)
    if pattern_height == 0:
        return set()
    pattern_width = len(pattern[0])

    margin = 2
    if (
        grid_width < pattern_width + 2 * margin
        or grid_height < pattern_height + 2 * margin
    ):
        print(
            "Error: grid too small for the '42' pattern; omitting the stamp.",
            file=sys.stderr,
        )
        return set()

    left_column = (grid_width - pattern_width) // 2
    top_row = (grid_height - pattern_height) // 2

    cells: set[tuple[int, int]] = set()
    for pattern_row in range(pattern_height):
        for pattern_column in range(pattern_width):
            if pattern[pattern_row][pattern_column] == 1:
                cells.add((
                    left_column + pattern_column,
                    top_row + pattern_row,
                ))
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

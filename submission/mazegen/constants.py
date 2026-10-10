"""Wall encoding, movement directions and the 42 bitmap."""
from __future__ import annotations

import sys

NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8
WALLS = (NORTH, EAST, SOUTH, WEST)
MOVE = {
    NORTH: (0, -1),
    EAST: (1, 0),
    SOUTH: (0, 1),
    WEST: (-1, 0),
}
OPPOSITE = {NORTH: SOUTH, EAST: WEST, SOUTH: NORTH, WEST: EAST}
LETTER = {NORTH: "N", EAST: "E", SOUTH: "S", WEST: "W"}

_PATTERN = (
    "#... .###",
    "#... ...#",
    "#..# .###",
    "#### .#..",
    "...# .#..",
    "...# .###",
)


def pattern_cells(width: int, height: int) -> set[tuple[int, int]]:
    """Return the centred 42 cells, or print a message if they do not fit."""
    pattern_height = len(_PATTERN)
    pattern_width = len(_PATTERN[0])
    if width < pattern_width + 4 or height < pattern_height + 4:
        print(
            "Grid too small for the 42 pattern; omitting it.",
            file=sys.stderr,
        )
        return set()

    left = (width - pattern_width) // 2
    top = (height - pattern_height) // 2
    return {
        (left + x, top + y)
        for y, row in enumerate(_PATTERN)
        for x, value in enumerate(row)
        if value == "#"
    }

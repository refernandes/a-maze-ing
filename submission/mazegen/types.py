"""Shared types and bit conventions for the ``mazegen`` package.

The file format assigns one bit to each cardinal wall.  Keeping the mapping in
one place avoids subtle disagreements between generation, solving, rendering,
and serialization code.
"""
from __future__ import annotations

from enum import IntEnum, Enum
from typing import TypedDict


class Direction(IntEnum):
    """Cardinal directions bit indices."""

    NORTH = 0  # 1 << 0 = 1
    EAST = 1   # 1 << 1 = 2
    SOUTH = 2  # 1 << 2 = 4
    WEST = 3   # 1 << 3 = 8


class Algorithm(str, Enum):
    """Supported maze generation algorithms."""

    DFS = "DFS"
    PRIM = "PRIM"
    KRUSKAL = "KRUSKAL"


class MazeConfig(TypedDict):
    """Maze configuration dictionary structure."""

    width: int
    height: int
    entry: tuple[int, int]
    exit_pos: tuple[int, int]
    perfect: bool
    output_file: str
    seed: int | None
    algorithm: Algorithm


# Wall mask constants
ALL_WALLS: int = 0x0F  # Binary 1111 = 15

# Direction coordinate offsets (dx, dy)
DELTA: dict[Direction, tuple[int, int]] = {
    Direction.NORTH: (0, -1),
    Direction.EAST: (1, 0),
    Direction.SOUTH: (0, 1),
    Direction.WEST: (-1, 0),
}

# Opposite directions mapping
OPPOSITE: dict[Direction, Direction] = {
    Direction.NORTH: Direction.SOUTH,
    Direction.EAST: Direction.WEST,
    Direction.SOUTH: Direction.NORTH,
    Direction.WEST: Direction.EAST,
}

# Character representation for cardinal directions
DIRECTION_CHARS: dict[Direction, str] = {
    Direction.NORTH: "N",
    Direction.EAST: "E",
    Direction.SOUTH: "S",
    Direction.WEST: "W",
}

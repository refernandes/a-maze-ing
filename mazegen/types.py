"""Type definitions for the A-Maze-ing project."""
from __future__ import annotations

from enum import Enum, IntEnum
from typing import TypedDict


class Direction(IntEnum):
    """Direction enumeration for maze generation.

    Values represent bit positions for wall encoding.
    """

    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


N_BIT: int = 1 << Direction.NORTH
E_BIT: int = 1 << Direction.EAST
S_BIT: int = 1 << Direction.SOUTH
W_BIT: int = 1 << Direction.WEST
ALL_WALLS: int = 15

OPPOSITE: dict[Direction, Direction] = {
    Direction.NORTH: Direction.SOUTH,
    Direction.SOUTH: Direction.NORTH,
    Direction.EAST: Direction.WEST,
    Direction.WEST: Direction.EAST,
}

DELTA: dict[Direction, tuple[int, int]] = {
    Direction.NORTH: (0, -1),
    Direction.EAST: (1, 0),
    Direction.SOUTH: (0, 1),
    Direction.WEST: (-1, 0),
}

DIRECTION_CHARS: dict[Direction, str] = {
    Direction.NORTH: "N",
    Direction.EAST: "E",
    Direction.SOUTH: "S",
    Direction.WEST: "W",
}


class Algorithm(Enum):
    """Supported maze generation algorithms."""

    DFS = "DFS"
    PRIM = "PRIM"
    KRUSKAL = "KRUSKAL"


class MazeConfig(TypedDict):
    """Configuration for maze generation."""

    width: int
    height: int
    entry: tuple[int, int]
    exit_pos: tuple[int, int]
    perfect: bool
    output_file: str
    seed: int | None
    algorithm: Algorithm
